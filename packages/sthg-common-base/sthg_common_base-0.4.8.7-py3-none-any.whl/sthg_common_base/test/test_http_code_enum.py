from sthg_common_base import ResponseEnum, BaseResponse
from sthg_common_base.response.httpCodeEnum import ResCode, HttpStatus


class CustomUserErrorEnum():
    Disk_Full_Error = ResCode("Disk_Full_Error", "磁盘错误！！", HttpStatus.BAD_REQUEST)

def test_custom_enum():

    ResponseEnum.update_response_enum(CustomUserErrorEnum)
    print(ResponseEnum.OK.getBusiCode)
    print(ResponseEnum.Disk_Full_Error.getBusiCode)
    print(ResponseEnum.OK.getBusiMsg)
    print(ResponseEnum.OK.getHttpCode)
    # 通过错误代码获取枚举项
    code = "AccessDenied"
    enum_member = ResponseEnum.from_code(code)
    if enum_member:
        print(enum_member.getBusiMsg)  # 输出: 您已被限制，请稍后再试！

    base_response=BaseResponse(resEnum=ResponseEnum.Disk_Full_Error,data=[])
    print(base_response)