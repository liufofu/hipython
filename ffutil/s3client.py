# -*-coding:utf-8 -*-
'''
author:virhuiai
nd_id:129600
e-mail:virhuiai@qq.com
Create Date:2014-12-5
'''

import time
import os

from hashlib import sha1
import hmac
import base64

import pycurl
import urlparse
import StringIO

"""
* nds 的s3存储 操作类
"""


class Client:
    # 连接参数，构造函数
    __host = ""
    __host_valid = ""
    __hostArrayTemp = []
    __access_key = ''
    __secret_key = ''
    __timeout = 60

    __ACL_PUBLIC = "public"
    __ACL_PRIVATE = "private"


    #失败的操作返回值
    __CODE_CRUL_ERROR = 500
    __CODE_INIT_HOST_ARRAY_ERROR = 500
    __CODE_EMPTY_HOST_ARRAY_ERROR = 500

    __CODE_XML_PARSE_ERROR = 500
    __CODE_PARAM_LACK = 500
    __CODE_PARAM_ERROR = 500
    __CODE_PARAM_OF_CEPH_LACK = 400
    __CODE_PARAM_OF_CEPH_ERROR = 400
    __CODE_FILE_RW_ERROR = 400
    #成功的操作返回值
    __CODE_CEPH_COMMON_SUCESS = 200
    __CODE_CEPH_DELETE_SUCESS = 204

    """
     * 给连接参数赋值
     * @param dict param 提供连接参数 键值说明如下：
     * <p>host：主机名 如：http://192.168.0.9</p>
     * <p>access_key： 如：8T3XFD2GREBG14F5YU5C</p>
     * <p>secret_key： 如：gY2oYJp+ovFot1Syz7ywVyMKCvdem/cobuXcBrRG</p>
    """

    def __init__(self, param):
        if 'host' not in param or 'access_key' not in param or 'secret_key' not in param:
            error_message = self.make_xml_error_message('ConnectParamLack')
            raise S3Exception(error_message, self.__CODE_PARAM_OF_CEPH_LACK)

        self.__host = param.get('host');
        self.__access_key = param.get('access_key')
        self.__secret_key = param.get('secret_key')
        if ('timeout' in param):
            self.__timeout = max(5, int(param.get('timeout')))

        if len(self.__host) == 0 or len(self.__access_key) == 0 or len(self.__secret_key) == 0:
            error_message = self.make_xml_error_message('ConnectParamError')
            raise S3Exception(error_message, self.__CODE_PARAM_OF_CEPH_ERROR)


    def make_xml_error_message(self, message):
        return '<?xml version="1.0" encoding="UTF-8"?><Error><Code>' + message + '</Code></Error>';

    '''
     *
     * 生成检验头部信息
     * @param string method http请求方法
     * @param  string uri
     * @return array
    '''

    def __make_signature_head(self, method, uri):
        HeadDate = time.strftime(u'%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
        h = hmac.new(self.__secret_key, method + '\n\n\n' + HeadDate + '\n' + uri, sha1).digest()
        signature = base64.b64encode(h).strip().encode('utf-8')

        return ['Date: ' + HeadDate, 'Authorization: AWS ' + self.__access_key + ':' + signature]

    '''
     * 传入一个字符串，修改它：串首有‘/’，尾部没有
     * @param string
     * @return string
    '''
    def backslash_prefix_do(self, a_string):
        return '/' + str(a_string).strip('/')
    '''
     * 传入一个字符串去除串尾‘/’
     * @param string
     * @return string
    '''
    def backslash_last_del(self, a_string):
        return str(a_string).rstrip('/')

    """
    curl返回请求结果
    @param param  <p>请求参数，说明如下:<p>
    <p>method：必须有 http方法</p>
    <p>path: 必须有 url的一部分，如http://www.nd.com.cn/2014/12/17 中的 /2014/12/17 部分 </p>
    <p>header_add:数组，只使用其每一个值,用完unset</p>
    <p>其他的键值请看$option_map数组，就是curl的选项</p>
    @return dict
    @throws S3Exception
    """
    def ceph_s3_curl_core(self, param):
        method = param['method']
        path = param['path']

        path = self.backslash_prefix_do(path)
        self.__host = self.backslash_last_del(self.__host)
        param['url'] = self.__host + path

        # 构造头部信息 param ['header_add']是列表格式
        header = self.__make_signature_head(method, path)
        if 'header_add' in param:
            if type(param['header_add']) == type([]):
                for value in param['header_add']:
                    header.append(value)
            param.pop('header_add')
        param['http_header'] = header


        '''
        *  param中为curl选项的值，
        *  如，param['method']的值是’GET',  option_map['method']值是CURLOPT_CUSTOMREQUEST
        *  则效果是：c.setopt(pycurl.CUSTOMREQUEST, 'GET')
        '''
        option_map = {
                     'method':          pycurl.CUSTOMREQUEST,
                     'url':             pycurl.URL,
                     'http_header':     pycurl.HTTPHEADER, # 设置头信息的地方
                     # 'return_transfer': pycurl.RETURNTRANSFER,#pycurl中无与php curl类似的选项
                     'post_fields':     pycurl.POSTFIELDS,
                     'put':             pycurl.PUT,
                     'in_file':         pycurl.INFILE,
                     'in_file_size':    pycurl.INFILESIZE,
                     'header':          pycurl.HEADER,
                     'no_body':         pycurl.NOBODY
        }

        c = pycurl.Curl()
        b = StringIO.StringIO()

        url_scheme=urlparse.urlparse(param['url'])[0]
        if url_scheme == 'https':
            c.setopt(pycurl.SSL_VERIFYPEER, 0)
            c.setopt(pycurl.SSL_VERIFYHOST, 0)

        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.TIMEOUT, self.__timeout)
        for param_key in param:
            param_value = param[param_key]
            if param_key in option_map:
                c.setopt(option_map[param_key], param_value)
        try:
            c.perform()
            return_value =  b.getvalue()
            c.getinfo(c.HTTP_CODE)
            http_code = c.getinfo(c.HTTP_CODE)
            if http_code == 500:
                error_message = self.make_xml_error_message('CurlMustDoReTry');
                raise S3Exception(error_message, self.__CODE_CRUL_ERROR)
            else:
                return {
                     'http_code' : http_code,
                     'xml' : return_value
                }
        except Exception:
            error_message = self.make_xml_error_message('CurlMustDoReTry');
            raise S3Exception(error_message, self.__CODE_CRUL_ERROR)



    """
    curl返回请求结果
    @param param  <p>请求参数，说明如下:<p>
    <p>method：必须有 http方法</p>
    <p>path: 必须有 url的一部分，如http://www.nd.com.cn/2014/12/17 中的 /2014/12/17 部分 </p>
    <p>header_add:数组，只使用其每一个值,用完unset</p>
    <p>其他的键值请看$option_map数组，就是curl的选项</p>
    @return dict
    @throws S3Exception
    """
    def ceph_s3_curl(self, param):
        # 必填参数信息判断与处理
        if 'method' not in param or 'path' not in param:
            error_message = self.make_xml_error_message('RequestParamLack')
            raise S3Exception(error_message, self.__CODE_PARAM_OF_CEPH_LACK)
        try:
            ceph_s3_curl_core_res = self.ceph_s3_curl_core(param)
            self.__host_valid = self.__host
            return ceph_s3_curl_core_res;
        except S3Exception,ex:
            self.init_host_array()
            while len(self.__host_valid) == 0 and len(self.__hostArrayTemp) > 0:
                try:
                    self.get_another_host()
                    ceph_s3_curl_core_res = self.ceph_s3_curl_core(param)
                    self.__host_valid = self.__host
                    self.get_another_host()
                    return ceph_s3_curl_core_res
                except S3Exception:
                    continue

            error_message = self.make_xml_error_message('FailedInTimesTry')
            raise S3Exception(error_message, self.__CODE_CRUL_ERROR)
    """
     * 多次尝试不同ip的准备动作，准备ip
    """
    def init_host_array(self):
        if(len(self.__hostArrayTemp) == 0):
            import urlparse
            import socket
            parse_url_res = urlparse.urlparse(self.__host)
            for i in socket.getaddrinfo(parse_url_res.netloc,None):
                self.__hostArrayTemp.append(i[4][0])

        print self.__hostArrayTemp

    """
     * 获取数组列表中的一个host
     * @throws S3Exception
    """
    def get_another_host(self):
        import random
        if(len(self.__hostArrayTemp) == 0):
            error_message = self.make_xml_error_message('EmptyHostArrayError')
            raise S3Exception(error_message, self.__CODE_EMPTY_HOST_ARRAY_ERROR)

        random.shuffle(self.__hostArrayTemp)
        another_host = self.__hostArrayTemp[0]
        self.__hostArrayTemp.pop(0)
        self.__host = another_host

    """
     * 获得uploadid 每次新请求，返回的值不一样
     * <p>这是分块上传申请id的第一步</p>
     * @param bucket bucket名
     * @param object 对象名
     * @return array 包含uploadid的数组，另一个函数调用本函数并解析出uploadid
     * @throws S3Exception
     """
    def initiate_multipart_upload(self, bucket, object):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)
        param = {
            'method'        : 'POST',
            'path'          : bucket + object + '?uploads',
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])
        else:
            return return_v

    """
     * 获得uploadid 每次新请求，返回的值不一样
     * 这是分块上传的第一步，申请id
     * @param bucket bucket名
     * @param object 对象名
     * @return string uploadid的值
     * @throws S3Exception
    """
    def get_uploadid(self, bucket, object):
        initiate_multipart_uploadRes = self.initiate_multipart_upload(bucket, object)
        from xml.dom.minidom import parse, parseString
        DOMTree = parseString(initiate_multipart_uploadRes['xml'])

        upload = DOMTree.getElementsByTagName("UploadId")
        return_v = upload[0].childNodes[0].nodeValue

        if len(return_v) == 0:
            error_message = self.make_xml_error_message('UploadidParseFailed')
            raise S3Exception(error_message, self.__CODE_XML_PARSE_ERROR)
        else:
            return return_v

    """
     * 获得分块上传的块的数量
     * @param fs_name 文件路径
     * @param per_size 每块的大小 单位 Mb
     * @return int
     * @throws S3Exception
    """
    def multipart_upload_calc_num(self, fs_name, per_size):
        import math
        if per_size < 5:
            error_message = self.make_xml_error_message('PartSizeMustLargeThanFive')
            raise S3Exception(error_message, self.__CODE_PARAM_OF_CEPH_ERROR)

        try:
            filesize = os.path.getsize(fs_name)
        except Exception:
            error_message = self.make_xml_error_message('FileSizeGetError')
            raise S3Exception(error_message, self.__CODE_FILE_RW_ERROR)

        return int(math.ceil(filesize / (per_size * 1024 * 1024 * 1.0)))

    """
     * 分块上传的某一块的上传，传入的是文件流（另一个函数是文件地址）
     * @param bucket bucket名
     * @param object 对象名
     * @param uploadid uploadid的值
     * @param partNumber 第几块
     * @param stream 文件流
     * @throws S3Exception
    """
    def multipart_upload_part_by_stream(self, bucket, object, uploadid, partNumber, stream):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)
        stream_size = len(stream)

        header_add = [
            'Content-Length:' + str(stream_size),
            'Content-type:'
        ]
        param = {
            'method'        : 'PUT',
            'path'          : bucket + object + '?partNumber=' + str(partNumber) + '&uploadId=' + uploadid,
             'post_fields'   : stream,
             'header_add'    : header_add
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])

    """
     * 分块上传的某一块的上传，传入的是文件地址（另一个函数是流）
     * @param bucket bucket名
     * @param object 对象名
     * @param uploadid uploadid名
     * @param partNumber  第几块
     * @param size 每个块的大小 单位是Mb
     * @param filePath 要上传文件的路径
     * @throws S3Exception
    """
    def multipart_upload_part(self, bucket, object, uploadid, partNumber, size, filePath):
        pos = partNumber - 1
        try:
            file_handle = open(filePath, 'rb')
        except Exception:
            error_message = self.make_xml_error_message('FileOpenError')
            raise S3Exception(error_message, self.__CODE_FILE_RW_ERROR)

        file_handle.seek(0)
        file_handle.seek(pos * size * 1024 * 1024)
        stream = file_handle.read(size * 1024 * 1024)
        return self.multipart_upload_part_by_stream(bucket, object, uploadid, partNumber, stream)

    """
     * 列出已经上传的部分的md5值
     * @param bucket bucket名
     * @param object 对象名
     * @param uploadid uploadid的值
     * @return array 其中的一个键值包含xml格式的所有已经上传部分的编号和校验码
     * @throws S3Exception
    """
    def list_multipart_upload_parts(self, bucket, object, uploadid):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)
        param = {
            'method'    : 'GET',
            'path'      : bucket + object + '?uploadId=' + uploadid,
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])
        else:
            return return_v

    """
     * 完成分块上传的块信息的拼接
     * @param $bucket bucket名
     * @param $object object名
     * @param $uploadid uploadid的值
     * @param $part_number_total 总的块数
     * @return string xml格式 用于合并已经上传部分
     * @throws S3Exception
    """
    def get_complete_multipart_xml_stream(self, bucket, object, uploadid, part_number_total):
        from xml.dom.minidom import parse, parseString
        # 获取所有已经上传的信息
        res = self.list_multipart_upload_parts(bucket, object, uploadid)

        DOMTree = parseString(res['xml'])
        DOMElement = DOMTree.documentElement
        resarray = {};
        upload = DOMElement.getElementsByTagName('PartNumber')
        etag = DOMElement.getElementsByTagName('ETag')
        for i in range(0, part_number_total, 1):
            resarray[upload[i].childNodes[0].nodeValue] = etag[i].childNodes[0].nodeValue

        begin = '<CompleteMultipartUpload>'
        end = '</CompleteMultipartUpload>'
        for i in range(0, part_number_total, 1):
          resarray[upload[i].childNodes[0].nodeValue] = etag[i].childNodes[0].nodeValue

        body = ''
        for PartNumber in resarray:
          ETag = resarray[PartNumber]
          body = body + '<Part><PartNumber>' + PartNumber + '</PartNumber><ETag>' + ETag + '</ETag></Part>'
        return begin + body + end

    """
     * 完成分块上传的最后一步
     * @param  string bucket bucket名
     * @param  string object object名
     * @param  string upload_id 上传id
     * @param  stream stream 传入的流，是所有块的信息 有第几块，相应的校验码  xml格式
     * @throws S3Exception
     * @return void
    """
    def complete_multipart_upload(self, bucket, object, upload_id, stream):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)


        header_add = [
            'Content-Length:' + str(len(stream)),
            'Content-type:'
        ]
        param = {
            'method'        : 'POST',
            'path'          : bucket + object + '?uploadId=' + upload_id,
            'post_fields'   : stream,
            'header_add'    : header_add
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])


    """
     * 获得已经上传函数的信息的动作   与  完成上传动作的合并
     * @param array 键值说明如下
     * <p>['bucket'];           bucket名</p>
     * <p>['object'];           object 名</p>
     * <p>['upload_file'];      要上传的文件的地址 如 /dev/shm/a.zip</p>
     * <p>['size'];             分块的每一块的大小</p>
     * @return void
    """
    def complete_multipart_upload_process(self, bucket, object, uploadid, part_number_total):
        stream = self.get_complete_multipart_xml_stream(bucket, object, uploadid, part_number_total)
        return self.complete_multipart_upload(bucket, object, uploadid, stream)

    """
     * 分块上传的单个调用函数：针对一个本地文件的分块上传
     * @param dict 各个键值如下次：
     * ['bucket'];           bucket名
     * ['object'];           object 名
     * ['upload_file'];      要上传的文件的地址 如 /dev/shm/a.zip
     * ['size'];             分块的每一块的大小 最小为5 否则出错
     * @return void
    """
    def multipart_upload_process(self, param):
        bucket = self.backslash_prefix_do(param['bucket'])
        object = self.backslash_prefix_do(param['object'])
        upload_file = param['upload_file']
        size = param['size']

        uploadid = self.get_uploadid(bucket, object)

        # 计算块数
        part_number_total = self.multipart_upload_calc_num(upload_file, size)
        for partNumber in range(1, part_number_total + 1, 1):
            self.multipart_upload_part(bucket, object, uploadid, partNumber, size, upload_file)

        return self.complete_multipart_upload_process(bucket, object, uploadid, part_number_total)

    '''
     * 获取bucket的acl
     * @param string bucket bucket名
     * @param string object object名
     * @param string position_val private或public
     * @param string uid 帐号id
     * @throws S3Exception
    '''
    def set_object_acl(self,bucket,object, position_val, uid):

        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)

        all_user_permission = """<Grant><Grantee xsi:type="Group" xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance"><URI>http://acs.amazonaws.com/groups/global/AllUsers</URI></Grantee><Permission>READ</Permission></Grant>"""
        if position_val == self.__ACL_PRIVATE:
            all_user_permission = ""

        stream = """<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/20060301/"><Owner><ID>"""\
                 + uid + """</ID></Owner><AccessControlList><Grant><Grantee xsi:type="CanonicalUser" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ID>""" +uid+\
                 """</ID></Grantee><Permission>FULL_CONTROL</Permission></Grant>"""\
                +all_user_permission+\
                 """</AccessControlList></AccessControlPolicy>"""

        header_add = [
            'Content-Length:' + str(len(stream)),
            'Content-type:'
        ]
        param = {
            'method'        : 'PUT',
            'path'          : bucket + object + '?acl',
            'post_fields'   : stream,
            'header_add'    : header_add
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])


    '''
     * 获取bucket的acl
     * @param string bucket bucket名
     * @throws S3Exception
    '''
    def get_object_acl(self,bucket, object):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)
        param = {
            'method'        : 'GET',
            'path'          : bucket + object + '?acl',
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])
        else:
            return return_v['xml']


    '''
     * 获取bucket的acl
     * @param string bucket bucket名
     * @throws S3Exception
    '''
    def get_bucket_acl(self,bucket):
        bucket = self.backslash_prefix_do(bucket)
        param = {
            'method'        : 'GET',
            'path'          : bucket + '?acl',
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])
        else:
            return return_v['xml']

    '''
     * 根据传入的流创建object
     * @param string bucket bucket名
     * @param string object 保存的对象名
     * @param stream stream 传入的流
     * @throws S3Exception
    '''
    def create_object(self, bucket, object, stream):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)
        header_add = [
            'Content-Length:' + str(len(stream)),
            'Content-type:'
        ]
        param = {
            'method'        : 'PUT',
            'path'          : bucket + object,
            'post_fields'   : stream,
            'header_add'    : header_add
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])

    """
     * 提供一个本地文件地址，上传用以创建object
     * @param string bucket bucket名
     * @param string object 对象保存的名字
     * @param string object_file  文件路径，如 /dev/shm/contents.htm
     * @throws S3Exception
    """
    def create_object_by_file(self, bucket, object, object_file):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)

        try:
            file_handle = open(object_file, 'rb')
        except Exception:
            error_message = self.make_xml_error_message('FileOpenError')
            raise S3Exception(error_message, self.__CODE_FILE_RW_ERROR)

        file_size = os.path.getsize(object_file)
        # print file_size
        #
        # param = {
        #     'method'        : 'PUT',
        #     'path'          : bucket + object,
        #     'put'           : 1,
        #     'in_file'       : file_handle,
        #     'in_file_size'  : file_size
        # }
        #
        # return_v = self.ceph_s3_curl(param)
        # if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
        #     raise S3Exception(return_v['xml'], return_v['http_code'])
        file_handle.seek(0)
        stream = file_handle.read(file_size)
        return self.create_object(bucket, object, stream)

    '''
     * 创建bucket
     * @param string bucket bucket名
     * @throws S3Exception
     * @return void
     '''
    def create_bucket(self, bucket):
        bucket = self.backslash_prefix_do(bucket)
        param = {
            'method': 'PUT',
            'path'  : bucket,
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])

    '''
     * 列出bucket 中的对象列表
     * @param bucket
     * @return string xml格式的
     * @throws S3Exception
    '''
    def list_bucket(self, bucket):
        bucket = self.backslash_prefix_do(bucket)
        param = {
            'method' : 'GET',
            'path' : bucket
        }
        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])
        else:
            return return_v['xml']

    '''
     * 获得对象信息：
     * @param bucket bucket 名
     * @param object 对象名
     * @return array header键对应的是object相关的信息，需要做解析,说明如下：
     * <p>Last-Modified: Tue, 16 Dec 2014 07:33:20 GMT 最后一次修改的时间</p>
     * <p>ETag: "296ab79bb0e6b305a21f964bd2ac8531"     文件的较验值值</p>
     * <p>Content-Length: 6                            文件大小，单位Kb</p><p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p>
     * @throws S3Exception
    '''
    def get_object_info(self, bucket, object):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)

        param = {
            'method' : 'HEAD',
            'path' : bucket + object,
            'header'  : 1,
            'no_body' : 1
        }

        return_v = self.ceph_s3_curl(param)
        return {
            'http_code' : return_v['http_code'],#200是有文件
            'header' : return_v['xml']
        }

    """
     * 取一个object 返回文件流
     * @param $bucket bucket名
     * @param $object 对象名
     * @return stream
     * @throws S3Exception
    """
    def get_object_stream(self, bucket, object):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)
        param = {
                'method'    : 'GET',
                'path'      : bucket + object
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], return_v['http_code'])
        else:
            return return_v['xml'] #stream


    """
     * 取一个object并保存到指定位置
     * @param $bucket bucket名
     * @param $object 对象名
     * @param $savePath 保存文件的地址，如：'d:/j.jpg'
     * @throws S3Exception
    """
    def get_object(self, bucket, object, savePath):
        return_value = self.get_object_stream(bucket, object)
        try:
            f = open(savePath, 'wb')
        except Exception:
            error_message = self.make_xml_error_message('FileOpenError')
            raise S3Exception(error_message, self.__CODE_FILE_RW_ERROR)

        f.write(return_value)

    """
     * 删除bucket
     * @param bucket bucket名
     * @throws S3Exception
    """
    def delete_bucket(self, bucket):
        bucket = self.backslash_prefix_do(bucket)
        param = {
                'method':'DELETE',
                'path'  :bucket
        }
        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_DELETE_SUCESS:
            raise S3Exception(return_v['xml'], self.__CODE_PARAM_OF_CEPH_LACK)

    """
     * 删除一个object
     * @param bucket bucket名
     * @param object 对象名
     * @throws S3Exception
    """
    def delete_object(self, bucket, object):
        bucket = self.backslash_prefix_do(bucket)
        object = self.backslash_prefix_do(object)
        param = {
                'method':'DELETE',
                'path'  :bucket + object
        }

        return_v = self.ceph_s3_curl(param)
        if return_v['http_code'] != self.__CODE_CEPH_DELETE_SUCESS:
            raise S3Exception(return_v['xml'], self.__CODE_PARAM_OF_CEPH_LACK)

    """
     * 列出所有的bucket
     * @return mixed
     * @throws S3Exception
    """
    def list_all(self):
        param = {
            'method'    : 'GET',
            'path'      : '/'
        }
        return_v = self.ceph_s3_curl(param)

        if return_v['http_code'] != self.__CODE_CEPH_COMMON_SUCESS:
            raise S3Exception(return_v['xml'], self.__CODE_PARAM_OF_CEPH_LACK)
        else:
            return return_v['xml']


'''
 * Class S3Exception S3 异常类
'''


class S3Exception(Exception):
    __code = 0;
    __message = "";

    def __init__(self, message, code=5):
        Exception.__init__(self)
        self.__code = code
        self.__message = message

    def get_code(self):
        return self.__code

    def get_message(self):
        return self.__message

    def get_error(self):
        return self.__class__.__name__ + ": [" + str(self.__code) + "]: {" + self.__message + "}\n"

    def __repr__(self):
        return self.__class__.__name__ + ": [" + str(self.__code) + "]: {" + self.__message + "}\n"

    def __str__(self):
        return self.__class__.__name__ + ": [" + str(self.__code) + "]: {" + self.__message + "}\n"