/* This is a proposed fix for the strain derivative calculation in fingerprint.c
   The original code computes incorrect strain derivatives.

   Original problematic code (lines 365-381):
   ```c
   if (lstress > 0 && dfpe != NULL) {
       double rx = rxyz_sphere[iats][0];
       double ry = rxyz_sphere[iats][1];
       double rz = rxyz_sphere[iats][2];
       if (ik == 0) {  // ∂/∂x
           dfpe[iat][0][iorb] += dot * rx;  // Wrong: should be dot * rx for εxx
           dfpe[iat][4][iorb] += dot * rz;  // Wrong: should be dot * rz for εxz
           dfpe[iat][5][iorb] += dot * ry;  // Wrong: should be dot * ry for εxy
       } else if (ik == 1) {  // ∂/∂y
           dfpe[iat][1][iorb] += dot * ry;
           dfpe[iat][3][iorb] += dot * rz;
           dfpe[iat][5][iorb] += dot * rx;
       } else if (ik == 2) {  // ∂/∂z
           dfpe[iat][2][iorb] += dot * rz;
           dfpe[iat][3][iorb] += dot * ry;
           dfpe[iat][4][iorb] += dot * rx;
       }
   }
   ```

   The issue is that this computes a mixed up version of strain derivatives.

   Correct strain derivative formula:
   For a homogeneous strain where r' = (I + ε) · r, we have:
   ∂r_i,α/∂ε_βγ = δ_αβ * r_i,γ

   Therefore:
   ∂fp/∂ε_αβ = Σ_j (∂fp/∂r_j,α) * r_j,β   (for diagonal components α=β)
   ∂fp/∂ε_αβ = Σ_j [(∂fp/∂r_j,α) * r_j,β + (∂fp/∂r_j,β) * r_j,α] / 2  (for off-diagonal)

   The corrected code should be:
*/

// Proposed fix for lines 365-381:
if (lstress > 0 && dfpe != NULL) {
    double rx = rxyz_sphere[iats][0];
    double ry = rxyz_sphere[iats][1];
    double rz = rxyz_sphere[iats][2];

    // dot = dfp[iat][iiat][ik][iorb] where ik = 0,1,2 for x,y,z

    if (ik == 0) {  // ∂fp/∂x
        dfpe[iat][0][iorb] += dot * rx;  // εxx: ∂fp/∂x * x
        dfpe[iat][5][iorb] += dot * ry;  // εxy: ∂fp/∂x * y (symmetric part)
        dfpe[iat][4][iorb] += dot * rz;  // εxz: ∂fp/∂x * z (symmetric part)
    } else if (ik == 1) {  // ∂fp/∂y
        dfpe[iat][1][iorb] += dot * ry;  // εyy: ∂fp/∂y * y
        dfpe[iat][5][iorb] += dot * rx;  // εxy: ∂fp/∂y * x (symmetric part)
        dfpe[iat][3][iorb] += dot * rz;  // εyz: ∂fp/∂y * z (symmetric part)
    } else if (ik == 2) {  // ∂fp/∂z
        dfpe[iat][2][iorb] += dot * rz;  // εzz: ∂fp/∂z * z
        dfpe[iat][4][iorb] += dot * rx;  // εxz: ∂fp/∂z * x (symmetric part)
        dfpe[iat][3][iorb] += dot * ry;  // εyz: ∂fp/∂z * y (symmetric part)
    }
}

/* Wait, actually the original code looks correct for the mapping!
   Let me reconsider...

   Voigt notation: [εxx, εyy, εzz, εyz, εxz, εxy] = [0, 1, 2, 3, 4, 5]

   For εxx: ∂fp/∂εxx = ∂fp/∂x * x  (only x components contribute)
   For εxy: ∂fp/∂εxy = ∂fp/∂x * y + ∂fp/∂y * x

   The original code does accumulate both parts for off-diagonal terms.

   So the issue might not be in the mapping but in:
   1. The positions rxyz_sphere being in a different coordinate system
   2. Missing factors or different strain convention
   3. The fingerprint derivatives themselves being computed incorrectly
*/