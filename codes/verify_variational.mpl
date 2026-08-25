# Exact Maple checks for the variational and multisymplectic section.
#
# Maple 2022 command-line use:
#     maple -q verify_variational.mpl
#
# The generic rifsimp result is printed together with its assumptions. Exact
# component identities are checked independently and do not depend on a
# generic division by A, r, eta, or ell0.

restart:
interface(prettyprint=0):
Failures := 0:

canon := proc(expr)
    local res;
    res := simplify(normal(expand(expr)), symbolic);
    return res;
end proc:

assertzero := proc(expr, tag::string)
    local res;
    res := canon(expr);
    if res <> 0 then
        printf("FAIL: %s\nResidual: %a\n", tag, res);
        global Failures;
        Failures := Failures+1;
        return NULL;
    end if;
    printf("PASS: %s\n", tag);
    return NULL;
end proc:

printf("Maple kernel version: %s\n", kernelopts(version)):
printf("Generic-sheet assumptions: r<>0, eta<>0, etaStar<>0, A<>0.\n"):
printf("Fold checks are evaluated separately at A=0; ell0=0 is retained.\n"):

# ----------------------------------------------------------------------
# 1. Point transformation, pulled-back Lagrangian, and fold.
# ----------------------------------------------------------------------

Phi := 2*eta + ell0*r^2*ln(eta/etaStar) - ell0*eta^2/2:
A := diff(Phi,eta):
B := diff(Phi,r):
Fr := B+A*etar:
Fz := A*etaz:
Leta := (Fr^2+Fz^2)/(2*r):

assertzero(A-(2+ell0*r^2/eta-ell0*eta), "Phi_eta=A"):
assertzero(B-2*ell0*r*ln(eta/etaStar), "Phi_r at fixed eta=B"):
assertzero(diff(Leta,etar)-A*Fr/r, "eta polymomentum pi^r"):
assertzero(diff(Leta,etaz)-A*Fz/r, "eta polymomentum pi^z"):
assertzero(diff(Leta,etar$2)-A^2/r, "velocity Hessian rr"):
assertzero(diff(diff(Leta,etar),etaz), "velocity Hessian rz"):
assertzero(diff(Leta,etaz$2)-A^2/r, "velocity Hessian zz"):

Av := subs(eta=r*v,A):
xminus := -2*v/(1-v^2):
assertzero(subs(ell0=xminus/r,Av), "fold equals lower density root"):
assertzero(subs(eta=r*v,diff(Phi,eta$2))
           +ell0*(1+1/v^2), "fold second derivative"):

# Functional Euler--Lagrange chain rule in independent jet coordinates.
DrJet := proc(expr)
    return diff(expr,r)+diff(expr,eta)*etar
           +diff(expr,etar)*etarr+diff(expr,etaz)*etarz;
end proc:
DzJet := proc(expr)
    return diff(expr,z)+diff(expr,eta)*etaz
           +diff(expr,etar)*etarz+diff(expr,etaz)*etazz;
end proc:
ELetaJet := diff(Leta,eta)-DrJet(diff(Leta,etar))
             -DzJet(diff(Leta,etaz)):
LPhiJet := DrJet(Fr)-Fr/r+DzJet(Fz):
assertzero(ELetaJet+A*LPhiJet/r, "Euler-Lagrange chain rule"):

# Existing exact VFE identity, repeated here as an independent gate.
unassign('vf'):
etaV := r*vf(r,z):
PhiV := 2*etaV+ell0*r^2*ln(etaV/etaStar)-ell0*etaV^2/2:
LPhiV := diff(PhiV,r$2)-diff(PhiV,r)/r+diff(PhiV,z$2):
EV := (2+ell0*r*(1/vf(r,z)-vf(r,z)))
      *(diff(vf(r,z),r$2)+diff(vf(r,z),z$2))
      +(2/r+3*ell0*(1/vf(r,z)-vf(r,z)))*diff(vf(r,z),r)
      -ell0*r*(1/vf(r,z)^2+1)
       *(diff(vf(r,z),r)^2+diff(vf(r,z),z)^2)
      +2*ell0/r-2*vf(r,z)/r^2:
assertzero(LPhiV-r*EV, "auxiliary identity L(Phi)=r E[v]"):

# ----------------------------------------------------------------------
# 2. Legendre transform and Poincare-Cartan pullback coefficients.
# ----------------------------------------------------------------------

etarInv := r*Pir/A^2-B/A:
etazInv := r*Piz/A^2:
Heta := Pir*etarInv+Piz*etazInv
        -subs({etar=etarInv,etaz=etazInv},Leta):
HetaTarget := r*(Pir^2+Piz^2)/(2*A^2)-B*Pir/A:
assertzero(Heta-HetaTarget, "eta De Donder-Weyl Hamiltonian"):

pr := Pir/A:
pz := Piz/A:
HF := r*(pr^2+pz^2)/2:
assertzero(pr*A-Pir, "Cartan pullback deta wedge dz"):
assertzero(-pz*A+Piz, "Cartan pullback deta wedge dr"):
assertzero(pr*B-HF+HetaTarget, "Cartan pullback dr wedge dz"):

# Fixed-boundary symplectic coefficient: dF=A deta and pi=A p. Evaluate
# both two-forms on two independent variations, including delta(A).
dF1 := A*deta1:
dF2 := A*deta2:
dPi1 := A*dp1+p*diff(A,eta)*deta1:
dPi2 := A*dp2+p*diff(A,eta)*deta2:
assertzero((dF1*dp2-dF2*dp1)-(deta1*dPi2-deta2*dPi1),
           "fixed-boundary symplectic trace pullback"):

# ----------------------------------------------------------------------
# 3. Multisymplectic, Noether, stress, and dilation identities.
# ----------------------------------------------------------------------

unassign('ff','gg','FF'):
Lf := u -> diff(u,r$2)-diff(u,r)/r+diff(u,z$2):

omegaR := (ff(r,z)*diff(gg(r,z),r)
           -gg(r,z)*diff(ff(r,z),r))/r:
omegaZ := (ff(r,z)*diff(gg(r,z),z)
           -gg(r,z)*diff(ff(r,z),z))/r:
assertzero(diff(omegaR,r)+diff(omegaZ,z)
           -(ff(r,z)*Lf(gg(r,z))-gg(r,z)*Lf(ff(r,z)))/r,
           "off-shell multisymplectic form formula"):

FFr := diff(FF(r,z),r):
FFz := diff(FF(r,z),z):
LFF := Lf(FF(r,z)):
Jzr := FFr*FFz/r:
Jzz := (FFz^2-FFr^2)/(2*r):
assertzero(diff(Jzr,r)+diff(Jzz,z)-FFz*LFF/r,
           "z-Noether divergence off shell"):

grad2 := FFr^2+FFz^2:
Trr := (FFr^2-FFz^2)/(2*r):
Trz := FFr*FFz/r:
Tzz := (FFz^2-FFr^2)/(2*r):
assertzero(diff(Trr,r)+diff(Trz,z)
           -FFr*LFF/r-grad2/(2*r^2),
           "radial stress divergence off shell"):
assertzero(diff(Trz,r)+diff(Tzz,z)-FFz*LFF/r,
           "vertical stress divergence off shell"):

Dr := r*Trr+z*Trz-FF(r,z)*FFr/(2*r):
Dz := r*Trz+z*Tzz-FF(r,z)*FFz/(2*r):
assertzero(diff(Dr,r)+diff(Dz,z)
           -(r*FFr+z*FFz-FF(r,z)/2)*LFF/r,
           "improved dilation divergence off shell"):
assertzero(diff(r*Trr+z*Trz,r)+diff(r*Trz+z*Tzz,z)
           -grad2/(2*r)-(r*FFr+z*FFz)*LFF/r,
           "Pohozaev local divergence off shell"):

# Formal z-Hamilton equations.
HamiltonResidual := r*(-diff(FFr/r,r))+diff(FFr,r)-FFr/r:
assertzero(HamiltonResidual, "z-Hamilton equations imply L(F)=0"):

# Exact auxiliary modes.
assertzero(Lf(1), "constant exact mode"):
assertzero(Lf(r^2), "quadratic exact mode"):
Mode := r*BesselJ(1,k*r)*cosh(k*z):
assertzero(simplify(Lf(Mode),Bessel), "Bessel-Hadamard exact mode"):

# ----------------------------------------------------------------------
# 4. Reduced Ernst variational equations.
# ----------------------------------------------------------------------

ErnstL := r*(qr^2+qz^2+cr^2+cz^2)/(2*q^2):
DrErnst := proc(expr)
    return diff(expr,r)+diff(expr,q)*qr+diff(expr,c)*cr
           +diff(expr,qr)*qrr+diff(expr,qz)*qrz
           +diff(expr,cr)*crr+diff(expr,cz)*crz;
end proc:
DzErnst := proc(expr)
    return diff(expr,z)+diff(expr,q)*qz+diff(expr,c)*cz
           +diff(expr,qr)*qrz+diff(expr,qz)*qzz
           +diff(expr,cr)*crz+diff(expr,cz)*czz;
end proc:
ELq := diff(ErnstL,q)-DrErnst(diff(ErnstL,qr))
       -DzErnst(diff(ErnstL,qz)):
ELc := diff(ErnstL,c)-DrErnst(diff(ErnstL,cr))
       -DzErnst(diff(ErnstL,cz)):
AxisLapQ := qrr+qr/r+qzz:
AxisLapC := crr+cr/r+czz:
ErnstFEq := q*AxisLapQ-(qr^2+qz^2-cr^2-cz^2):
ErnstChiEq := q*AxisLapC-2*(qr*cr+qz*cz):
assertzero(ELq+r*ErnstFEq/q^3,
           "Ernst f Euler-Lagrange equation"):
assertzero(ELc+r*ErnstChiEq/q^3,
           "Ernst chi Euler-Lagrange equation"):

# ----------------------------------------------------------------------
# 5. rifsimp audit of the harmonic-translation determining equation.
# ----------------------------------------------------------------------

try
    RifInput := diff(h(r,z),r$2)-diff(h(r,z),r)/r
                +diff(h(r,z),z$2):
    RIF := DEtools:-rifsimp([RifInput=0]):
    assertzero(lhs(RIF['Solved'][1])-rhs(RIF['Solved'][1])-RifInput,
               "rifsimp harmonic-translation determining system"):
    printf("rifsimp output (generic branch r<>0): %a\n", eval(RIF)):
catch:
    printf("FAIL: rifsimp determining-system audit\n"):
    printf("rifsimp exception: %a\n", lastexception):
    Failures := Failures+1:
end try:

if Failures=0 then
    printf("All exact Maple variational/multisymplectic checks passed.\n"):
else
    printf("Maple certificate failed %d check(s).\n", Failures):
    error "Maple variational/multisymplectic certificate failed";
end if:
