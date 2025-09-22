"""
点云相关工具
"""

from copy import deepcopy
import re
from functools import reduce
from pathlib import Path
from typing import Generator, NamedTuple

import numpy as np
from returns.io import impure_safe
from returns.result import Failure, Result, Success, safe

from fyuneru.geometry3d import SElement, to_homogeneous_matrix


class PcdHeaderMeta(NamedTuple):
    data_start: int
    header_bytes: bytes


class PcdHeader(NamedTuple):
    """PCD 头结构"""

    VERSION: str
    FIELDS: list[str]
    SIZE: list[int]
    TYPE: list[str]
    COUNT: list[int]
    WIDTH: int
    HEIGHT: int
    VIEWPOINT: list[int]
    POINTS: int
    DATA: str


class PcdHeaderCol(NamedTuple):
    idx: int
    field: str
    type: str
    count: int
    size: int


class Pcd(NamedTuple):
    pc: np.ndarray
    header: PcdHeader


@impure_safe
def read_head_bytes(file: Path, num_bytes: int) -> bytes:
    """读取文件前num_bytes字节"""
    with file.open("rb") as f:
        return f.read(num_bytes)


@impure_safe
def get_pcd_head_meta(file: Path, start_bytes) -> PcdHeaderMeta:
    """
    取 PCD 头元信息

    支持的 DATA 格式：
        DATA ascii
        DATA binary
        DATA binary_compressed

    Args:
        file: PCD 文件路径
        cat_bytes: 读取头部的最大字节数

    Returns:
        PcdHeaderMeta
    """
    # 读取头部字节（解包 Result -> bytes）
    origin_head_bytes = read_head_bytes(file, start_bytes).unwrap()._inner_value

    # 正则匹配 DATA 行
    data_pattern = rb"DATA\s+(ascii|binary|binary_compressed)\s*\n"
    match = re.search(data_pattern, origin_head_bytes)
    if not match:
        raise ValueError("PCD ERROR: DATA line not found or invalid format")

    # 数据起始位置（换行后一个字节）
    data_start = match.end()

    return PcdHeaderMeta(
        data_start=data_start, header_bytes=origin_head_bytes[:data_start]
    )


def convert_pcd_header_to_str(pcd_header: PcdHeader) -> str:
    return (
        "# .PCD v0.7 - Point Cloud Data file format\n"
        f"VERSION {pcd_header.VERSION}\n"
        + f"FIELDS {' '.join(pcd_header.FIELDS)}\n"
        + f"SIZE {' '.join(map(str, pcd_header.SIZE))}\n"
        + f"TYPE {' '.join(pcd_header.TYPE)}\n"
        + f"COUNT {' '.join(map(str, pcd_header.COUNT))}\n"
        + f"WIDTH {pcd_header.WIDTH}\n"
        + f"HEIGHT {pcd_header.HEIGHT}\n"
        + f"VIEWPOINT {' '.join(map(str, pcd_header.VIEWPOINT))}\n"
        + f"POINTS {pcd_header.POINTS}\n"
        + f"DATA {pcd_header.DATA}\n"
    )


def convert_str_to_pcd_header(header_str: str) -> PcdHeader:
    HEADER_PATTERN = re.compile(
        r"^(VERSION|FIELDS|SIZE|TYPE|COUNT|WIDTH|HEIGHT|VIEWPOINT|POINTS|DATA)"
    )
    """将字符串转换为pcd头"""
    header_lines = [line.strip() for line in header_str.split("\n") if line.strip()]
    header = {}
    for line in header_lines[1:]:
        match = HEADER_PATTERN.match(line)
        if not match:
            raise ValueError(f"Invalid header line: {line}")
        parts = line.split()
        key = match.group(0)
        header[key] = parts[1:] if len(parts) > 2 else parts[1]
    header["POINTS"] = int(header["POINTS"])
    header["WIDTH"] = int(header["WIDTH"])
    header["HEIGHT"] = int(header["HEIGHT"])
    return PcdHeader(**header)


@safe
def parse_pcd_header(meta: PcdHeaderMeta) -> PcdHeader:
    """解析pcd头"""
    header_str = meta.header_bytes.decode(encoding="utf-8")
    return convert_str_to_pcd_header(header_str)


@safe
def build_dtype(
    fields: list[str], types: list[str], sizes: list[int], counts: list[int]
) -> np.dtype:
    """构建pcd numpy结构
    Args:
        fields (list): 字段名
        types (list): 类型
        sizes (list): 大小
        counts (list): 数量
    Raises:
        ValueError: 不支持的类型
    Returns:
        np.dtype: numpy结构
    """
    TYPE_MAP = {
        ("U", 1): np.uint8,
        ("U", 2): np.uint16,
        ("U", 4): np.uint32,
        ("U", 8): np.uint64,
        ("I", 1): np.int8,
        ("I", 2): np.int16,
        ("I", 4): np.int32,
        ("I", 8): np.int64,
        ("F", 4): np.float32,
        ("F", 8): np.float64,
    }
    field_dtypes = [TYPE_MAP[(t, int(s))] for t, s in zip(types, sizes)]
    dtype = reduce(
        lambda acc, zip_value: acc
        + [(f"{zip_value[0]}_{i}", zip_value[1]) for i in range(int(zip_value[2]))],
        zip(fields, field_dtypes, counts),
        [],
    )
    return np.dtype(dtype)


@impure_safe
def read_pcd(pcd_file: Path, start_bytes: int = 1024) -> Result[Pcd, ValueError]:
    """读取pcd文件
    Args:
        pcd_file: pcd文件路径
        start_bytes: 读取头部的最大字节数
    Returns:
        tuple[np.ndarray, PcdHeader]
    """
    meta = get_pcd_head_meta(pcd_file, start_bytes).unwrap()._inner_value
    header = parse_pcd_header(meta).unwrap()
    data_type = header.DATA.lower()
    data = None
    dtype = build_dtype(header.FIELDS, header.TYPE, header.SIZE, header.COUNT).unwrap()

    match data_type:
        case "binary":
            data = __read_pcd_binary(pcd_file, dtype, meta.data_start)
        case _:
            raise ValueError(f"Unsupported data type: {data_type}")

    return Pcd(pc=np.array(data.view(dtype).tolist()), header=header)


def __read_pcd_binary(file_path: Path, dtype: np.dtype, data_start: int) -> np.ndarray:
    return np.fromfile(file=file_path, dtype=dtype, offset=data_start)


def __write_pcd_binary(
    file: Path, header: PcdHeader
) -> Generator[None, np.ndarray, None]:
    """流式写入二进制PCD文件的生成器
    Args:
        file: PCD文件路径
        header: PCD头信息，包含字段定义

    Yields:
        None: 每次yield后等待接收点云数据
    """
    # 根据头部信息构建dtype
    dtype = build_dtype(header.FIELDS, header.TYPE, header.SIZE, header.COUNT).unwrap()

    with file.open("wb") as f:
        header_data = convert_pcd_header_to_str(header).encode("utf-8")
        f.write(header_data)

        while True:
            pc_data: np.ndarray = yield
            if pc_data is None:
                break
            f.write(array_to_structured(pc_data, dtype).tobytes(order="C"))


def array_to_structured(pc_array: np.ndarray, dtype: np.dtype) -> np.ndarray:
    """将二维数组转换为 build_dtype 构建的结构化数组"""
    N = pc_array.shape[0]
    arr = np.zeros(N, dtype=dtype)
    col_start = 0
    for name in dtype.names:
        field_dtype, _ = dtype.fields[name]  # 获取字段的 dtype 和偏移量
        # 判断这个字段是标量还是数组
        if field_dtype.shape == ():
            count = 1
        else:
            count = field_dtype.shape[0]
        cols = pc_array[:, col_start : col_start + count]
        if count == 1:
            # 标量字段（转成该字段基础类型）
            arr[name] = cols[:, 0].astype(field_dtype)
        else:
            # 向量字段（直接转成目标类型）
            arr[name] = cols.astype(field_dtype.base)
        col_start += count
    return arr


def get_pcd_writer(file: Path, header: PcdHeader):
    """获取已初始化的PCD写入器

    Args:
        file: PCD文件路径
        header: PCD头信息

    Returns:
        已初始化的写入器生成器，可直接使用send()方法写入数据
    """
    data_type = header.DATA.lower()
    match data_type:
        case "binary":
            writer = __write_pcd_binary(file, header)
            next(writer)  # 初始化写入器，写入头部信息
            return writer
        case _:
            raise ValueError(f"Unsupported data type: {data_type}")


def transform_pc(pc: np.ndarray, T: np.ndarray) -> np.ndarray:
    """
    三维点 转换到box坐标系
    """
    pc_homo = np.hstack([pc, np.ones((pc.shape[0], 1))])
    return (T @ pc_homo.T).T[:, :3]


def is_in_box_mask(
    pc: np.ndarray, box_center: SElement, box_size: list[float]
) -> np.ndarray:
    """
    返回布尔掩码，表示哪些点在box内。
    pc: (N, 3) ndarray
    box_center: 中心+旋转 (SElement)
    box_size: [xmin, xmax, ymin, ymax, zmin, zmax]（在box坐标系下）
    如果某个范围值为0，则不参与这方向的限制（相当于无限大）
    """
    # 世界坐标系 -> box局部坐标系
    T_glo_box = to_homogeneous_matrix(box_center)
    T_box_glo = np.linalg.inv(T_glo_box)
    pc_in_box_element = transform_pc(pc=pc, T=T_box_glo)

    # 处理 0 作为无限范围
    bounds = box_size.copy()
    if bounds[0] == 0:
        bounds[0] = -np.inf
    if bounds[1] == 0:
        bounds[1] = np.inf
    if bounds[2] == 0:
        bounds[2] = -np.inf
    if bounds[3] == 0:
        bounds[3] = np.inf
    if bounds[4] == 0:
        bounds[4] = -np.inf
    if bounds[5] == 0:
        bounds[5] = np.inf

    # 分别判断每个方向
    mask_x = (pc_in_box_element[:, 0] >= bounds[0]) & (
        pc_in_box_element[:, 0] <= bounds[1]
    )
    mask_y = (pc_in_box_element[:, 1] >= bounds[2]) & (
        pc_in_box_element[:, 1] <= bounds[3]
    )
    mask_z = (pc_in_box_element[:, 2] >= bounds[4]) & (
        pc_in_box_element[:, 2] <= bounds[5]
    )

    return mask_x & mask_y & mask_z


@safe
def add_column(pc: np.ndarray, col: np.ndarray) -> np.ndarray:
    return np.column_stack([pc, col])


def append_pcd_header(origin_header: PcdHeader, col_header: PcdHeaderCol) -> PcdHeader:
    header = deepcopy(origin_header)
    header.FIELDS.append(col_header.field)
    header.COUNT.append(col_header.count)
    header.SIZE.append(col_header.size)
    header.TYPE.append(col_header.type)
    return header


def write_pcd(file: Path, header: PcdHeader, pc: np.ndarray):
    pcd_writer = get_pcd_writer(file=file, header=header)
    pcd_writer.send(pc)
    pcd_writer.close()
