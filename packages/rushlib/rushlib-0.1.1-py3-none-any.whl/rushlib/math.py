import math
from typing import Union

Number = Union[int, float]


class Vector2:
    """二维向量类"""

    __slots__ = ('x', 'y')

    def __init__(self, x: Number = 0, y: Number = 0):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self) -> str:
        return f"Vec2({self.x}, {self.y})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return False
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Number) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: Number) -> 'Vector2':
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Number) -> 'Vector2':
        if abs(scalar) < 1e-10:
            raise ZeroDivisionError("Division by near-zero scalar")
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> 'Vector2':
        return Vector2(-self.x, -self.y)

    def __abs__(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def dot(self, other: 'Vector2') -> float:
        """点积"""
        return self.x * other.x + self.y * other.y

    def cross(self, other: 'Vector2') -> float:
        """叉积（标量）"""
        return self.x * other.y - self.y * other.x

    def length(self) -> float:
        """向量长度"""
        return abs(self)

    def length_squared(self) -> float:
        """向量长度的平方"""
        return self.x * self.x + self.y * self.y

    def normalized(self) -> 'Vector2':
        """单位向量"""
        length = self.length()
        if length < 1e-10:
            return Vector2(0, 0)
        return self / length

    def normalize(self) -> None:
        """将向量单位化（原地操作）"""
        length = self.length()
        if length < 1e-10:
            self.x, self.y = 0, 0
        else:
            self.x /= length
            self.y /= length

    def distance_to(self, other: 'Vector2') -> float:
        """到另一个向量的距离"""
        return (self - other).length()

    def angle(self) -> float:
        """向量的角度（弧度）"""
        return math.atan2(self.y, self.x)

    def rotated(self, angle: float) -> 'Vector2':
        """旋转指定弧度后的向量"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def rotate(self, angle: float) -> None:
        """旋转指定弧度（原地操作）"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        self.x, self.y = x, y

    def lerp(self, other: 'Vector2', t: float) -> 'Vector2':
        """线性插值"""
        t = max(0.0, min(1.0, t))  # 限制t在[0,1]范围内
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )

    def copy(self) -> 'Vector2':
        """返回向量的副本"""
        return Vector2(self.x, self.y)

    @classmethod
    def from_angle(cls, angle: float, length: float = 1.0) -> 'Vector2':
        """从角度和长度创建向量"""
        return cls(math.cos(angle) * length, math.sin(angle) * length)

    @classmethod
    def zero(cls) -> 'Vector2':
        """零向量"""
        return cls(0, 0)

    @classmethod
    def one(cls) -> 'Vector2':
        """全1向量"""
        return cls(1, 1)

    @classmethod
    def up(cls) -> 'Vector2':
        """上向量"""
        return cls(0, 1)

    @classmethod
    def down(cls) -> 'Vector2':
        """下向量"""
        return cls(0, -1)

    @classmethod
    def left(cls) -> 'Vector2':
        """左向量"""
        return cls(-1, 0)

    @classmethod
    def right(cls) -> 'Vector2':
        """右向量"""
        return cls(1, 0)


class Vector3:
    """三维向量类"""

    __slots__ = ('x', 'y', 'z')

    def __init__(self, x: Number = 0, y: Number = 0, z: Number = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self) -> str:
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector3):
            return False
        return (math.isclose(self.x, other.x) and
                math.isclose(self.y, other.y) and
                math.isclose(self.z, other.z))

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: Number) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: Number) -> 'Vector3':
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Number) -> 'Vector3':
        if abs(scalar) < 1e-10:
            raise ZeroDivisionError("Division by near-zero scalar")
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> 'Vector3':
        return Vector3(-self.x, -self.y, -self.z)

    def __abs__(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def dot(self, other: 'Vector3') -> float:
        """点积"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vector3') -> 'Vector3':
        """叉积（向量）"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self) -> float:
        """向量长度"""
        return abs(self)

    def length_squared(self) -> float:
        """向量长度的平方"""
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalized(self) -> 'Vector3':
        """单位向量"""
        length = self.length()
        if length < 1e-10:
            return Vector3(0, 0, 0)
        return self / length

    def normalize(self) -> None:
        """将向量单位化（原地操作）"""
        length = self.length()
        if length < 1e-10:
            self.x, self.y, self.z = 0, 0, 0
        else:
            self.x /= length
            self.y /= length
            self.z /= length

    def distance_to(self, other: 'Vector3') -> float:
        """到另一个向量的距离"""
        return (self - other).length()

    def lerp(self, other: 'Vector3', t: float) -> 'Vector3':
        """线性插值"""
        t = max(0.0, min(1.0, t))  # 限制t在[0,1]范围内
        return Vector3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t
        )

    def copy(self) -> 'Vector3':
        """返回向量的副本"""
        return Vector3(self.x, self.y, self.z)

    @classmethod
    def zero(cls) -> 'Vector3':
        """零向量"""
        return cls(0, 0, 0)

    @classmethod
    def one(cls) -> 'Vector3':
        """全1向量"""
        return cls(1, 1, 1)

    @classmethod
    def up(cls) -> 'Vector3':
        """上向量"""
        return cls(0, 1, 0)

    @classmethod
    def down(cls) -> 'Vector3':
        """下向量"""
        return cls(0, -1, 0)

    @classmethod
    def left(cls) -> 'Vector3':
        """左向量"""
        return cls(-1, 0, 0)

    @classmethod
    def right(cls) -> 'Vector3':
        """右向量"""
        return cls(1, 0, 0)

    @classmethod
    def forward(cls) -> 'Vector3':
        """前向量"""
        return cls(0, 0, 1)

    @classmethod
    def back(cls) -> 'Vector3':
        """后向量"""
        return cls(0, 0, -1)


vec2 = Vector2
vec3 = Vector3
