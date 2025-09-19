import math as m
import hashlib
import sys
import datetime
from typing import Optional, Tuple, Callable, Any
import importlib
import binascii
import base64
import time
from random import randint

# constant defined
pi = 3.1415926535898   #Cicurmference Ratio, The ratio of the Cicurmference to the diameter
e = 2.7182818284591   #Euler Number, Equal lim{x->inf}(1+1/x)^x or sum^{inf}_{x=0}:1/(x!)
nan = m.nan   #Not a Number
c = 299792458   #Speed of light
ly = 9460730472580800   #Light Years
unitol = 1e-6
naturalsum = -(1/12)   #1+2+3+…+∞=-1/12=ζ(-1)
atan1 = pi / 4
deg = pi / 180
h = 6.62607015e-34
hbar = h/(2*pi)
TCMB = 2.72548
a0 = -273.15
ec = 1.602176634e-19
u0 = 1.25663706212e-6
e0 = 1/(u0 * (c**2))
phi = (1 + m.sqrt(5)) / 2
cphi = ((1 + m.sqrt(5))*1j)/2
psi = 3.3598856662432
superphi = 1.4655712318768
pho = 1.3247179572448
triphi = 1.8392867552142
vis = 1.1319882487943
et = 0.7025840583106
lochs = 0.8685890302381
k0 = 2.6854520010653
gamma = 0.57721566490153
mm = 0.2614972128476
legd = 1
omega = 0.5671432904098   #Ωe^Ω=1, Omega equal W(1) or LambertW(1)
gelf = e ** pi
gs = 2 ** (m.sqrt(2))
cahen = 0.6434105462228
catal = (pi**2)/16
apery = 1.2020569031596
walli = pi/2
somos = 1.6616879496336
MRBp = 0.1878596424621
MRBn = -0.8121403575379
B2 = 1.902160583104
B4 = 0.875058838
niven = 1.7052111401334
laplimit = 0.66274341935
P = 2.2955871493926
varpi = 2.6220575542921
varpiprime = 1.3110287771461
Gs = varpi/pi
AGM = 1/Gs
b = 0.76422365011921
conway = 1.3035772690343
PTM = 0.4124540336401
C10 = 0.1234567891011
C2 = 0.5862477352306
CE = 0.2357111317192
primepho = 0.4146825098511
kc = 0.7947058128783
A = 1.3063778838631
FR = 2.8077702420285
R = 8.7000366252088
Kpho = 1/R
dottie = 0.7390851332152
degdottie = 0.9998477415459
foias = 1.1874520318972
EB = 1.6066951524153
H = 0.5164541487973
Basel = (pi**2)/6
w_half = 0.3517337112488   #W(1/2)
ebar = (-2)*w_half   #Universal exponential constant, e^ebar=ebar^2
hjbar = 2.1978071864361   #Hyperbolic Constant, Original Symbol is ђ, Satisfy sinh(ђ) equal cosh(sqrt(ђ))
djh = hjbar
goldang = 360/(phi ** 2)
sliver = 1 + m.sqrt(2)
cooper = (1 + m.sqrt(3)) / 2   #Cooper ratio
serical = 1 + atan1   #Serical ratio
alpha = (ec ** 2)/(4 * pi * e0 * hbar * c)
cosmol = 1.1e-108
bek = 1e123   #Beksten Bound
kB = 1.380649e-23
ae = 0.00115965218076e-3
me = (ec**2)/(4*pi*e0) * (hbar)/(2*c*ae)
mu = 1836.1562734311998
mp = mu*me
R_inf = 1.0973731568508e-7
NA = 6.02214076e23
le = h/(me * c)
M_ea = 5.9722e+24
R_ea = 6371008.7714
G = 6.67430151567820e-11
g = (G*M_ea)/(R_ea**2)
M_sun = 1.989e30
alphaG = (G * (me **2))/(hbar * c)
ke = 1/(4*pi*e0)
H0 = 69.94
dlcosmol = (cosmol * (c**2))/(H0 ** 2)
dlR_inf = (R_inf * h * c)/(me * (c**2))
mn = 1.674927498042e-27
a0 = 5.2917721093112e-11
eV = 1.602176634e-19
sigma = 5.670374419e-8
F = NA * ec
lp = m.sqrt((hbar * G)/(c**3))
tp = lp / c
Ep = m.sqrt((hbar * (c**5))/G)
dp = (c**5)/(hbar * (G**2))
pp = (c**5) / G
mp = m.sqrt((hbar * c)/G)
qp = m.sqrt(4*pi*e0*hbar*c)
Tp = (mp*(c**2))/kB
Pp = Ep/(lp**3)
year = 365.242190402197
month = year/12
smonth = 29.530588853
tmonth = 27.32158224184
pc = 30856778149136.73
pm = 60 * pc
ph = 60 * pm
pd = 24 * ph
pw = 7 * pd
pmth = month * pd
py = year * pd
pcy = 100 * py
kpc = 1000 * pc
Mpc = 1000 * kpc
Gpc = 1000 * Mpc
Tpc = 1000 * Gpc
AU = 149597870700
delta = 4.669201609103
sfalpha = 2.5029078750959
wb = 2.8977719552841
tH = Mpc / H0
lG = tH * H0 * lp  #Great Gup, Length of our Universe
pytha = m.sqrt(2)
sqrt2 = m.sqrt(2)
sqrt3 = m.sqrt(3)
sqrt5 = m.sqrt(5)
sqrt_half = m.sqrt(1 / 2)
rad = 180 / pi
tau = 2 * pi
infty = float('inf')
inf = m.inf
magicang = m.atan(sqrt2)
sha256 = hashlib.sha256()

# basic function mapping(first define)
sin = m.sin
cos = m.cos
tan = m.tan
cot = lambda x: 1/m.tan(x)
sec = lambda x: 1/m.cos(x)
csc = lambda x: 1/m.sin(x)
asin = m.asin
acos = m.acos
atan = m.atan
acot = lambda x: m.atan(1/x)
asec = lambda x: m.acos(1/x)
acsc = lambda x: m.asin(1/x)
sinh = m.sinh
cosh = m.cosh
tanh = m.tanh
coth = lambda x: 1/m.tanh(x)
sech = lambda x: 1/m.cosh(x)
csch = lambda x: 1/m.sinh(x)
asinh = m.asinh
acosh = m.acosh
atanh = m.atanh
acoth = lambda x: m.atanh(1/x)
asech = lambda x: m.acosh(1/x)
acsch = lambda x: m.asinh(1/x)
isqrt = m.isqrt
root = m.sqrt
sqrt = m.sqrt
floor = m.floor
ceil = m.ceil
sum = m.fsum
prod = lambda iterable: m.prod(list(iterable))
exp = m.exp
ln = m.log
fact = m.factorial
factorial = m.factorial
gamma = m.gamma
#function defined
def hascycle(head: Any) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False


def findcyclestart(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if fast == slow:
            break
        else:
            return None
    p = head
    while p != slow:
        p = p.next
        slow = slow.next
    return p


def ispalindrome(head):
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next
    prev = None
    curr = slow
    while curr:
        n = curr.next
        curr.next = prev
        prev = curr
        curr = n
    left = head
    right = prev
    while right:
        if left.val != right.val:
            return False
        left = left.next
        right = right.next
    return True


def log(n,base=2):
    return m.log(n,base)


def lg(n):
    return m.log(n,10)


def prime(n):
    if n < 1:
        raise ValueError("n must be a positive integer (n≥1)")
    primes = [2]
    candidate = 3
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 2
    return primes[-1]


def hypot(a: float, b: float) -> float:
    return m.sqrt((a ** 2) + (b ** 2))


def K_to_C(Tkep):
    return Tkep + a0


def C_to_F(TC):
    return (TC * 1.8) + 32


def F_to_C(TF):
    return (TF - 32)/1.8


def C_to_K(TC):
   return TC - a0


def F_to_K(TF):
    return ((TF - 32)/1.8)-a0


def K_to_F(Tkep):
    return C_to_F(K_to_C(Tkep))


def find_int_hypot(time: int) -> Optional[Tuple[float, float]]:
    if not isinstance(time, int) or time <= 0:
        return None

    def helper(t: int) -> Optional[Tuple[float, float]]:
        if t % 2 == 1:
            s1 = (t ** 2 - 1) / 2
            return (s1, s1 + 1)
        else:
            res = helper(t // 2)
            return (res[0] * 2, res[1] * 2) if res else None

    return helper(time)


def fixed_point(
    f: Callable[[float], float],
    x0: float,
    tol: float = 1e-6,
    max_iter: int = 1000
) -> float:
    x = x0
    for i in range(max_iter):
        x_next = f(x)
        if abs(x_next - x) < tol:
            print(f"converged after {i+1} iterations")
            return x_next
        x = x_next
    print(f"Maximum number of iterations {max_iter} reached, no convergence")
    return x

def kepler(ei,Ei):
    return Ei - ei*m.sin(Ei)


def lambert_w(z, branch=0, tol=1e-12, max_iter=100):
    min_z = -1 / m.e
    if z < min_z:
        raise ValueError(f"z must be ≥ -1/e ≈ {min_z:.12f}, got z={z}")
    
    if branch == 0:
        if z == 0:
            return 0.0
        elif z > 0:
            w = m.log(z + 1)
        else:
            w = -1 + m.sqrt(2 * (m.e * z + 1))
    elif branch == -1:
        if z >= 0:
            raise ValueError("Branch -1 only supports z < 0")
        w = m.log(-z) - m.log(-m.log(-z))
    else:
        raise ValueError("Only branch=0 or branch=-1 is supported")
    
    for _ in range(max_iter):
        ew = m.exp(w)
        f = w * ew - z
        f_prime = ew * (w + 1)
        if abs(f_prime) < 1e-16:
            break
        delta = f / f_prime
        w -= delta
        if abs(delta) < tol:
            return w
    
    raise RuntimeWarning(f"Failed to converge after {max_iter} iterations. Current error: {abs(delta)}")


def clamp(x: float, low: float, high: float) -> float:
    return max(low, min(x, high))


def isimport(mod: str) -> bool:
    return mod in sys.modules


def cheektime(month: int, day: int = None) -> bool:
    now = datetime.datetime.now()
    if day is None:
        return month == now.month
    return month == now.month and day == now.day


def has_mod(mod_name: str) -> bool:
    try:
        importlib.import_module(mod_name)
        return True
    except ImportError:
        return False
    except Exception:
        return False


def sind(d):
    return sin(deg * d)


def cosd(d):
    return cos(deg * d)


def tand(d):
    return tan(deg * d)


def cotd(d):
    return cot(deg * d)


def secd(d):
    return sec(deg * d)


def cscd(d):
    return csc(deg * d)


def asind(d):
    return asin(deg * d)


def acosd(d):
    return acos(deg * d)


def atand(d):
    return atan(deg * d)


def acotd(d):
    return acot(deg * d)


def asecd(d):
    return asec(deg * d)


def acscd(d):
    return acsc(deg * d)


def sindh(d):
    return sinh(deg * d)


def cosdh(d):
    return cosh(deg * d)


def tandh(d):
    return tanh(deg * d)


def cotdh(d):
    return coth(deg * d)


def secdh(d):
    return sech(deg * d)


def cscdh(d):
    return csch(deg * d)


def asindh(d):
    return asinh(deg * d)


def acosdh(d):
    return acosh(deg * d)


def atandh(d):
    return atanh(deg * d)


def acotdh(d):
    return acoth(deg * d)


def asecdh(d):
    return asech(deg * d)


def acscdh(d):
    return acsch(deg * d)


def pm(a, b):
    return a + b, a - b


def mp(a, b):
    return a - b, a + b


def sfrt(x):
    return m.pow(x, 1/x)


def delta(a, b, c):
    return (b ** 2) - (4 * a * c)


def quadratic(a, b, c):
    return (pm((-b), m.sqrt(delta(a, b, c)))) / (2 * a)


def succ(x):
    return x + 1


def s(x):
    return x + 1


def pred(x):
    return x - 1

def p(x):
    return x - 1


def digit(number, n=0):
    if n < 0:
        scale = 10 ** (-n)
        shifted = abs(number) * scale
        integer_part = int(shifted)
        return integer_part % 10
    else:
        scale = 10 ** n
        scaled = int(abs(number) // scale)
        return scaled % 10


def sha256hash(con):
    global sha256
    constr = str(con)
    sha256.update(constr.encode('utf-8'))
    return sha256.hexdigest()


def isprime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    max_divisor = int(m.isqrt(n)) + 1
    for d in range(3, max_divisor, 2):
        if n % d == 0:
            return False
    return True


def ismsprime(p):
    if not isprime(p):
        return False
    m_p = (1 << p) - 1
    return isprime(m_p)


def isgsprime(z):
    m_val = z.real
    n_val = z.imag
    if not (isinstance(m_val, int) or m_val.is_integer()) or not (isinstance(n_val, int) or n_val.is_integer()):
        return False
    m_val = int(m_val)
    n_val = int(n_val)
    norm = m_val ** 2 + n_val ** 2
    if norm == 1:
        return False
    if m_val == 0 or n_val == 0:
        p = abs(m_val) if m_val != 0 else abs(n_val)
        return isprime(p) and (p % 4 == 3)
    else:
        return isprime(norm)


def lens(con):
    return len(str(con))


def cont(a, b, c=""):
    return str(a) + str(b) + str(c)


def caesar(text, key, decy=False):
    real_key = key % 26
    if decy:
        real_key = -real_key
    result = []
    for char in text:
        if char.isupper():
            shifted = ord(char) + real_key
            if shifted > 90:
                shifted -= 26
            elif shifted < 65:
                shifted += 26
            result.append(chr(shifted))
        elif char.islower():
            shifted = ord(char) + real_key
            if shifted > 122:
                shifted -= 26
            elif shifted < 97:
                shifted += 26
            result.append(chr(shifted))
        else:
            result.append(char)
    return ''.join(result)


def easy_caesar(light_or_dark, key=3, ups=False):
    if not isinstance(key, int):
        return None
    
    realkey = key % 26
    
    if not ups:
        realinput = light_or_dark.lower()
    else:
        realinput = light_or_dark.upper()
    
    if ups:
        alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    else:
        alphabet = list('abcdefghijklmnopqrstuvwxyz')
    
    result = []
    
    for char in realinput:
        if char in alphabet:
            original_index = alphabet.index(char)
            encrypted_index = (original_index + realkey) % 26
            result.append(alphabet[encrypted_index])
        else:
            result.append(char)
    
    return ''.join(result)


def tangent(x,deltax,func):
    return (func(x+deltax)-func(x))/deltax


def differentiate(x,func,dx=1e-6):
    return tangent(x,dx,func)


def sigmoid(x):
    return 1/(1+(exp(-x)))


def ntanh(x):
    return (m.tanh(x)+1)/2


def ReLU(x):
    return max(0,x)


def LReLU(x,a=0.1):
    abar = a % 1
    return max((abar*x),x)


def LeakyReLU(x,a=0.1):
    abar = a % 1
    return max((abar*x),x)


def CDF(x):
    xbar = 0.5*x
    cons = m.sqrt(2/m.pi)
    xbarbar = x + (0.044715 * (x**3))
    return xbar * (1+m.tanh(cons * xbarbar))


def GELU(x):
    return x*CDF(x)


def number(n,tol=6,rd=True):
    if rd:
        return round(n,tol)
    else:
        return int(n * (10**tol))/tol


def absdiff(a,b):
    return abs(a-b)

#Advance Class:Quaternion

class quaternion:
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)
    
    def __add__(self, other):
        if isinstance(other, quaternion):
            return quaternion(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
        return quaternion(self.x + other, self.y + other, self.z + other, self.w + other)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, quaternion):
            return quaternion(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
        return quaternion(self.x - other, self.y - other, self.z - other, self.w - other)
    
    def __rsub__(self, other):
        return quaternion(other - self.x, other - self.y, other - self.z, other - self.w)
    
    def __mul__(self, other):
        if isinstance(other, quaternion):
            w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
            x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
            y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
            z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
            return quaternion(x, y, z, w)
        return quaternion(self.x * other, self.y * other, self.z * other, self.w * other)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, other):
        if isinstance(other, quaternion):
            return self * other.inverse()
        return quaternion(self.x / other, self.y / other, self.z / other, self.w / other)
    
    def __rtruediv__(self, other):
        return self.inverse() * other
    
    def __neg__(self):
        return quaternion(-self.x, -self.y, -self.z, -self.w)
    
    def __eq__(self, other):
        if not isinstance(other, quaternion):
            return False
        return (m.isclose(self.x, other.x) and m.isclose(self.y, other.y) and 
                m.isclose(self.z, other.z) and m.isclose(self.w, other.w))
    
    def __abs__(self):
        return m.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
    
    def norm(self):
        return abs(self)
    
    def conjugate(self):
        return quaternion(-self.x, -self.y, -self.z, self.w)
    
    def inverse(self):
        n2 = self.x**2 + self.y**2 + self.z**2 + self.w**2
        if n2 == 0:
            return quaternion()
        return quaternion(-self.x/n2, -self.y/n2, -self.z/n2, self.w/n2)
    
    def normalize(self):
        n = abs(self)
        if n == 0:
            return quaternion()
        return quaternion(self.x/n, self.y/n, self.z/n, self.w/n)
    
    def to_euler(self):
        x, y, z, w = self.x, self.y, self.z, self.w
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = m.atan2(sinr_cosp, cosr_cosp)
        
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = m.copysign(m.pi / 2, sinp)
        else:
            pitch = m.asin(sinp)
        
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = m.atan2(siny_cosp, cosy_cosp)
        
        return roll, pitch, yaw
    
    @classmethod
    def from_euler(cls, roll, pitch, yaw):
        cy = m.cos(yaw * 0.5)
        sy = m.sin(yaw * 0.5)
        cp = m.cos(pitch * 0.5)
        sp = m.sin(pitch * 0.5)
        cr = m.cos(roll * 0.5)
        sr = m.sin(roll * 0.5)
        
        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy
        
        return cls(x, y, z, w)
    
    @classmethod
    def from_axis_angle(cls, axis, angle):
        axis = [float(a) for a in axis]
        norm = m.sqrt(sum(a*a for a in axis))
        if norm == 0:
            return cls()
        axis = [a/norm for a in axis]
        s = m.sin(angle/2)
        return cls(axis[0]*s, axis[1]*s, axis[2]*s, m.cos(angle/2))
    
    def to_axis_angle(self):
        if abs(self.w) > 1:
            q = self.normalize()
        else:
            q = self
        
        angle = 2 * m.acos(q.w)
        s = m.sqrt(1 - q.w*q.w)
        if s < 0.001:
            axis = [1.0, 0.0, 0.0]
        else:
            axis = [q.x/s, q.y/s, q.z/s]
        
        return axis, angle
    
    def __str__(self):
        return f"({self.x}i + {self.y}j + {self.z}k + {self.w})"
    
    def __repr__(self):
        return f"quaternion({self.x}, {self.y}, {self.z}, {self.w})"
