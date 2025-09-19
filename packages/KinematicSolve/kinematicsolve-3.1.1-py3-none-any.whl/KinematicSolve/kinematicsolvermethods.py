"""
kinematicSolve

A Python module for solving kinematics problems, supporting:
- Algebra-based uniform acceleration motion (UAM)
- Symbolic calculus using sympy
- Numeric evaluation over time intervals

Functions:
- KinematicSolverUAM(SUVAT): Solve algebraic UAM problems.
- kinematicSolverSymbolic(SVA, conV=None, conD=None): Solve symbolically with derivatives and integrals.
- kinematicSolverNumeric(completeSVA, t1, t2): Evaluate numeric results from symbolic solutions.

Requirements:
- Python 3.8+
- sympy
"""
import math
import sympy as sp

t = sp.symbols('t')
def parseInfo(condition):
    x = condition[2:condition.find(")")]
    y = condition[condition.find("=")+1:]
    x = float(x)
    y = float(y)
    return [x, y]

def KinematicSolverUAM(SUVAT):
    """
    Solves uniform acceleration motion (UAM) problems algebraically.

    Parameters
    ----------
    SUVAT : list of length 5
        [S, U, V, A, T] where:
        - S : displacement (float, meters) or None
        - U : initial velocity (float, m/s) or None
        - V : final velocity (float, m/s) or None
        - A : acceleration (float, m/s²) or None
        - T : time (float, seconds) or None
        Use None for unknown variables.

    Returns
    -------
    list
        Completed list [S, U, V, A, T] with all unknowns calculated.

    Notes
    -----
    - Time (T) must be non-zero when used in calculations.
    - Handles all combinations of known/unknown variables for UAM.
    
    Example
    -------
    >>> SUVAT = [None, 0, 20, 2, None]
    >>> KinematicSolverUAM(SUVAT)
    [50.0, 0, 20, 2, 10.0]
    """
    newSUVAT = SUVAT.copy()
    if SUVAT[0] == None:
        if SUVAT[1] is not None and SUVAT[3] is not None and SUVAT[4] is not None:
            newSUVAT[0] = SUVAT[1]*SUVAT[4]+(1/2)*SUVAT[3]*SUVAT[4]*SUVAT[4]
        else:
            if SUVAT[3] == 0:
                newSUVAT[0] = SUVAT[1]*SUVAT[4]
            else:
                newSUVAT[0] = ((SUVAT[2]*SUVAT[2])-(SUVAT[1]*SUVAT[1]))/(2*SUVAT[3])
    if SUVAT[1] is None:
        if SUVAT[2] is not None and SUVAT[3] is not None and SUVAT[4] is not None:
            newSUVAT[1] = SUVAT[2] - SUVAT[3] * SUVAT[4]
        elif SUVAT[2] is None:
            newSUVAT[1] = (newSUVAT[0] - (1/2)*SUVAT[3]*SUVAT[4]*SUVAT[4])/SUVAT[4]
        elif SUVAT[4] is None:
            newSUVAT[1] = (SUVAT[2]*SUVAT[2])-(2*SUVAT[3]*newSUVAT[0])
            newSUVAT[1] = math.sqrt(newSUVAT[1])
    if SUVAT[2] is None:
        if SUVAT[1] is not None and SUVAT[3] is not None and SUVAT[4] is not None:
            newSUVAT[2]= newSUVAT[1]+SUVAT[3]*SUVAT[4]
        elif SUVAT[4] is None:
            newSUVAT[2] = newSUVAT[1]*newSUVAT[1]+ 2* SUVAT[3] * SUVAT[0]
            newSUVAT[2] = math.sqrt(newSUVAT[2])
    if SUVAT[3] is None:
        if SUVAT[1] is not None and SUVAT[2] is not None and SUVAT[4] is not None:
            newSUVAT[3] = (newSUVAT[2]-newSUVAT[1])/SUVAT[4]
        elif SUVAT[2] is None:
            newSUVAT[3] = (newSUVAT[0] - (SUVAT[4]*newSUVAT[1]))/((1*SUVAT[4]*SUVAT[4])/2)
        else:
            newSUVAT[3] = ((newSUVAT[2]*newSUVAT[2])-(newSUVAT[1]*newSUVAT[1]))/(2*newSUVAT[0])
    if SUVAT[4] is None:
        if SUVAT[1] is not None and SUVAT[2] is not None and SUVAT[3] is not None:
            newSUVAT[4] = (newSUVAT[2]-newSUVAT[1])/ newSUVAT[3]
        else:
            if newSUVAT[3] == 0:
                newSUVAT[4] = newSUVAT[0]/newSUVAT[1]
            else:
                t1 = (-newSUVAT[1] + math.sqrt((newSUVAT[1]*newSUVAT[1])+2*newSUVAT[3]*newSUVAT[0]))/newSUVAT[3]
                t2 = (-newSUVAT[1] - math.sqrt((newSUVAT[1]*newSUVAT[1])+2*newSUVAT[3]*newSUVAT[0]))/newSUVAT[3]
                if t1>=t2:
                    newSUVAT[4] = t1
                else:
                    newSUVAT[4] = t2
    return newSUVAT
def kinematicSolverSymbolic(SVA):
    """
    Solves kinematics symbolically using derivatives and integrals, applying 
    initial conditions if provided.

    Parameters
    ----------
    SVA : list
        A list of three elements [displacement, velocity, acceleration] where each
        element can be a sympy expression or None if unknown.

    Returns
    -------
    list
        A list [displacement_expr, velocity_expr, acceleration_expr] where unknowns
        have been computed symbolically.

    Notes
    -----
    - If displacement is provided, velocity and acceleration are computed via differentiation.
    - If velocity is provided, displacement is computed via integration.
    - If acceleration is provided, velocity and displacement are computed via integration.

    Example
    -------
    >>> import sympy as sp
    >>> t = sp.symbols('t')
    >>> SVA = [None, 5*t, None]  # [Displacement, Velocity, Acceleration]
    >>> kinematicSolverSymbolic(SVA)
    [5*t, 5, 0]
    """
    t = sp.symbols("t")
    C1 = sp.symbols('C1')
    C2 = sp.symbols('C2')
    if SVA[0] is not None:
        if SVA[1] is None:
            SVA[1] = sp.diff(SVA[0], t, n=1)
        if SVA[2] is None:
            SVA[2] = sp.diff(SVA[0], t, n=2)
    if SVA[1] is not None:
        if SVA[2] is None:
            SVA[2] = sp.diff(SVA[1], t, n=1)
        if SVA[0] is None:
            SVA[0] = sp.integrate(SVA[1], t) + C2
    if SVA[2] is not None:
        if SVA[1] is None:
            SVA[1] = sp.integrate(SVA[2], t) + C1
        if SVA[0] is None:
            SVA[0] = sp.integrate(SVA[1], t) + C2
    newSVA = SVA.copy()
    return newSVA
def kinematicSolverSymbolicCondition(SVA, conV, conD):
    """
    Computes symbolic expressions for position, velocity, and acceleration 
    based on partial input and initial conditions.

    Parameters:
        SVA (list): A list of three elements [S, V, A], where each element 
                    can be a SymPy expression or None. Represents 
                    [position, velocity, acceleration]. None indicates 
                    the quantity is unknown and should be computed.
        conV (str): A string representing an initial velocity condition, 
                    e.g., "v(0)=5". Used to solve for constants of integration.
        conD (str): A string representing an initial position condition, 
                    e.g., "s(0)=10". Used to solve for constants of integration.

    Returns:
        list: A list of SymPy expressions [S(t), V(t), A(t)] with all 
              unknowns computed and constants of integration substituted.
              
    Notes:
        - If acceleration is provided, velocity and position are computed via integration.
        - If velocity is provided, acceleration and position are computed via differentiation/integration.
        - If position is provided, velocity and acceleration are computed via differentiation.
        - Constants of integration (C1, C2) are automatically solved using conV and conD.
    """
    t = sp.symbols("t")
    C1 = sp.symbols('C1')
    C2 = sp.symbols('C2')
    vInfo = parseInfo(conV)
    dInfo = parseInfo(conD)
    if SVA[0] is not None:
        if SVA[1] is None:
            SVA[1] = sp.diff(SVA[0], t, n=1)
        if SVA[2] is None:
            SVA[2] = sp.diff(SVA[0], t, n=2)
    if SVA[1] is not None:
        if SVA[2] is None:
            SVA[2] = sp.diff(SVA[1], t, n=1)
        if SVA[0] is None:
            SVA[0] = sp.integrate(SVA[1], t) + C2
    if SVA[2] is not None:
        if SVA[1] is None:
            SVA[1] = sp.integrate(SVA[2], t) + C1
        if SVA[0] is None:
            SVA[0] = sp.integrate(SVA[1], t) + C2
    arrayVal = [None, None]
    arrayVal[1] = SVA[1].subs(C1, 0)
    arrayVal[1] = arrayVal[1].subs(t, vInfo[0])
    vConst = vInfo[1] - arrayVal[1]
    SVA[1] = SVA[1].subs(C1, vConst)
    SVA[0] = SVA[0].subs(C1, vConst)
    arrayVal[0] = SVA[0].subs(C2, 0)
    arrayVal[0] = arrayVal[0].subs(t, dInfo[0])
    dConst = dInfo[1] - arrayVal[0]
    SVA[0] = SVA[0].subs(C2, dConst)
    return SVA
def kinematicSolverNumeric(SVA, conV, conD , t1, t2):
    """
    Computes the numeric change in position, velocity, and acceleration 
    over a time interval [t1, t2] using symbolic expressions.

    Parameters:
        SVA (list): A list of three elements [S, V, A], where each element 
                    can be a SymPy expression or None. Represents 
                    [position, velocity, acceleration].
        conV (str): A string representing an initial velocity condition, 
                    e.g., "v(0)=5".
        conD (str): A string representing an initial position condition, 
                    e.g., "s(0)=10".
        t1 (float or int): The starting time for the interval.
        t2 (float or int): The ending time for the interval.

    Returns:
        list: A list of numeric values [ΔS, ΔV, ΔA] representing the change 
              in position, velocity, and acceleration over the interval [t1, t2].

    Notes:
        - Uses kinematicSolverSymbolicCondition to generate symbolic expressions.
        - Substitutes t2 and t1 into each expression and returns the difference.
        - For constant acceleration, ΔA will always be 0.
    """
    newSVA = kinematicSolverSymbolicCondition(SVA, conV, conD) 
    t = sp.symbols("t") 
    for i in range (0, 3): 
        newSVA[i] = newSVA[i].subs(t, t2) - newSVA[i].subs(t, t1) 
    return newSVA
