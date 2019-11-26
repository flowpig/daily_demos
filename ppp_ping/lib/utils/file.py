import os, fnmatch
import gzip
import filecmp


class File(object):

    @classmethod
    def find(cls, pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

    @classmethod
    def get_last_file_modify_time(cls, pattern, path):
        last_modify_time = 0
        files = cls.find(pattern, path)
        for f in files:
            modify_time = os.stat(f).st_mtime
            if modify_time > last_modify_time:
                last_modify_time = modify_time
        return last_modify_time

    @classmethod
    def compress_file(cls, input, output):
        f_in = open(input)
        f_out = gzip.open(output, 'wb')
        f_out.writelines(f_in)
        f_in.close()
        f_out.close()

    @classmethod
    def write_compress_file(cls, file_name, content):
        with gzip.open(file_name, "wb") as f_out:
            f_out.write(content)

    @classmethod
    def write_file(cls, file_name, content):
        with open(file_name, "wb") as out:
            out.write(content)
        os.chmod(file_name, 0777)

    @classmethod
    def get_last_modify_file_and_time(cls, pattern, path = "/"):
        last_modify_time = 0
        l_file = None
        files = cls.find(pattern, path)
        for f in files:
            modify_time = os.stat(f).st_mtime
            if modify_time > last_modify_time:
                last_modify_time = modify_time
                l_file = f
        return l_file, last_modify_time

    @classmethod
    def remove_files(cls, file_list):
        for f in file_list:
            os.remove(f)

    @classmethod
    def compare_file(cls, old, new):
        return filecmp.cmp(old, new)
