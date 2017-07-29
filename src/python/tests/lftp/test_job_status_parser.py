# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest

from lftp import LftpJobStatusParser, LftpJobStatus


class TestLftpJobStatusParser(unittest.TestCase):
    def test_size_to_bytes(self):
        self.assertEqual(1000, LftpJobStatusParser._size_to_bytes("1000b"))
        self.assertEqual(1000, LftpJobStatusParser._size_to_bytes("1000 b"))
        self.assertEqual(1000, LftpJobStatusParser._size_to_bytes("1000B"))
        self.assertEqual(1024, LftpJobStatusParser._size_to_bytes("1kb"))
        self.assertEqual(1024, LftpJobStatusParser._size_to_bytes("1 kb"))
        self.assertEqual(1536, LftpJobStatusParser._size_to_bytes("1.5kb"))
        self.assertEqual(2048, LftpJobStatusParser._size_to_bytes("2KiB"))
        self.assertEqual(1048576, LftpJobStatusParser._size_to_bytes("1mb"))
        self.assertEqual(1048576, LftpJobStatusParser._size_to_bytes("1 mb"))
        self.assertEqual(1572864, LftpJobStatusParser._size_to_bytes("1.5mb"))
        self.assertEqual(2097152, LftpJobStatusParser._size_to_bytes("2MiB"))
        self.assertEqual(1073741824, LftpJobStatusParser._size_to_bytes("1gb"))
        self.assertEqual(1073741824, LftpJobStatusParser._size_to_bytes("1 gb"))
        self.assertEqual(1610612736, LftpJobStatusParser._size_to_bytes("1.5gb"))
        self.assertEqual(2147483648, LftpJobStatusParser._size_to_bytes("2GiB"))

    def test_eta_to_seconds(self):
        self.assertEqual(100, LftpJobStatusParser._eta_to_seconds("100s"))
        self.assertEqual(100*60, LftpJobStatusParser._eta_to_seconds("100m"))
        self.assertEqual(100*60*60, LftpJobStatusParser._eta_to_seconds("100h"))
        self.assertEqual(100*24*60*60, LftpJobStatusParser._eta_to_seconds("100d"))
        self.assertEqual(1*24*60*60+1, LftpJobStatusParser._eta_to_seconds("1d1s"))
        self.assertEqual(1*24*60*60+1*60, LftpJobStatusParser._eta_to_seconds("1d1m"))
        self.assertEqual(1*24*60*60+1*60*60, LftpJobStatusParser._eta_to_seconds("1d1h"))
        self.assertEqual(1*24*60*60+1*60*60+1*60+1, LftpJobStatusParser._eta_to_seconds("1d1h1m1s"))
        self.assertEqual(1*60*60+1*60+1, LftpJobStatusParser._eta_to_seconds("1h1m1s"))
        self.assertEqual(1*60+1, LftpJobStatusParser._eta_to_seconds("1m1s"))

    def test_empty_output_1(self):
        output = ""
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        self.assertEqual(0, len(statuses))

    def test_empty_output_2(self):
        output = """
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        self.assertEqual(0, len(statuses))

    def test_empty_output_3(self):
        output = """
        [1] Done (queue (sftp://someone:@localhost))
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        self.assertEqual(0, len(statuses))

    def test_queued_items(self):
        """Queued items, no jobs running"""
        output = """
        [0] queue (sftp://someone:@localhost)
        sftp://someone:@localhost/home/someone
        Queue is stopped.
        Commands queued:
         1. mirror -c /tmp/test_lftp/remote/a /tmp/test_lftp/local/
         2. pget -c /tmp/test_lftp/remote/c -o /tmp/test_lftp/local/
         3. mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/
         4. mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/
         5. mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden = [
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="a",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="c",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c")
        ]
        self.assertEqual(len(golden), len(statuses))
        self.assertEqual(golden, statuses)

    def test_queued_items_with_quotes(self):
        """Queue with quotes"""
        output = """
        [0] queue (sftp://someone:@localhost)
        sftp://someone:@localhost/home/someone
        Queue is stopped.
        Commands queued:
         1. mirror -c "/tmp/test_lftp/remote/b s s" /tmp/test_lftp/local/
         2. pget -c "/tmp/test_lftp/remote/a s s" -o /tmp/test_lftp/local/
         3. mirror -c "/tmp/test_lftp/remote/b s s" "/tmp/test_lftp/local/"
         4. pget -c "/tmp/test_lftp/remote/a s s" -o "/tmp/test_lftp/local/"
         5. mirror -c /tmp/test_lftp/remote/b "/tmp/test_lftp/local/"
         6. pget -c /tmp/test_lftp/remote/a -o "/tmp/test_lftp/local/"
         7. mirror -c "/tmp/test_lftp/remote//b" "/tmp/test_lftp/local/"
         8. pget -c "/tmp/test_lftp/remote//a" -o "/tmp/test_lftp/local/"
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden = [
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b s s",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="a s s",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b s s",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="a s s",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="a",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="a",
                          flags="-c"),
        ]
        self.assertEqual(len(golden), len(statuses))
        self.assertEqual(golden, statuses)

    def test_queue_and_jobs_1(self):
        """Queued items, parallel jobs running, multiple files, multiple chunks"""
        output = """
        [1] queue (sftp://someone:@localhost)  -- 15.8 KiB/s
        sftp://someone:@localhost/home/someone
        Now executing: [2] mirror -c /tmp/test_lftp/remote/a /tmp/test_lftp/local/ -- 17k/26M (0%) 5.0 KiB/s
                -[3] mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/ -- 35k/394k (8%) 10.8 KiB/s
        Commands queued:
         1. pget -c /tmp/test_lftp/remote/c -o /tmp/test_lftp/local/
         2. mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/
         3. mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/
        [2] mirror -c /tmp/test_lftp/remote/a /tmp/test_lftp/local/  -- 17k/26M (0%) 5.0 KiB/s
        \\transfer `aa'
        `aa' at 2976 (12%) 997b/s eta:22s [Receiving data]
        \\transfer `ab'
        `ab', got 13733 of 25165824 (0%) 4.0K/s eta:1h45m
        \chunk 0-6291456
        `ab' at 4362 (0%) 1.1K/s eta:92m [Receiving data]
        \chunk 18874368-25165823
        `ab' at 18877569 (0%) 1001b/s eta:1h45m [Receiving data]
        \chunk 12582912-18874367
        `ab' at 12585895 (0%) 997b/s eta:1h45m [Receiving data]
        \chunk 6291456-12582911
        `ab' at 6294643 (0%) 999b/s eta:1h45m [Receiving data]
        [3] mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/  -- 35k/394k (8%) 10.8 KiB/s
        \\transfer `bb'
        `bb', got 12333 of 131072 (9%) 3.9K/s eta:30s
        \chunk 0-32768
        `bb' at 2970 (2%) 996b/s eta:30s [Receiving data]
        \chunk 98304-131071
        `bb' at 101288 (9%) 998b/s eta:30s [Receiving data]
        \chunk 65536-98303
        `bb' at 68727 (9%) 1001b/s eta:30s [Receiving data]
        \chunk 32768-65535
        `bb' at 35956 (9%) 998b/s eta:30s [Receiving data]
        \mirror `ba'  -- 23k/263k (8%) 6.9 KiB/s
       \\transfer `ba/baa'
        `baa', got 9342 of 131072 (7%) 2.9K/s
        \chunk 0-32768
        `baa' at 3192 (2%) 998b/s eta:30s [Receiving data]
        \chunk 98304-131071
        `baa' at 98304 (0%) [ssh_exchange_identification: Connection closed by remote host]
        \chunk 65536-98303
        `baa' at 68721 (9%) 998b/s eta:30s [Receiving data]
        \chunk 32768-65535
        `baa' at 35733 (9%) 993b/s eta:30s [Receiving data]
        \\transfer `ba/bab'
        `bab', got 13128 of 131072 (10%) 4.0K/s eta:30s
        \chunk 0-32768
        `bab' at 4170 (3%) 1.1K/s eta:26s [Receiving data]
        \chunk 98304-131071
        `bab' at 101297 (9%) 1001b/s eta:30s [Receiving data]
        \chunk 65536-98303
        `bab' at 68525 (9%) 999b/s eta:30s [Receiving data]
        \chunk 32768-65535
        `bab' at 35744 (9%) 997b/s eta:30s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="c",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(17*1024, 26*1024*1024, 0, 5*1024, None)
        golden_job1.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(2976, None, 12, 997, 22)
        )
        golden_job1.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(13733, 25165824, 0, 4*1024, 1*3600+45*60)
        )
        golden_job2 = LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="b",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(35*1024, 394*1024, 8, 11059, None)
        golden_job2.add_active_file_transfer_state(
            "bb", LftpJobStatus.TransferState(12333, 131072, 9, 3993, 30)
        )
        golden_job2.add_active_file_transfer_state(
            "ba/baa", LftpJobStatus.TransferState(9342, 131072, 7, 2969, None)
        )
        golden_job2.add_active_file_transfer_state(
            "ba/bab", LftpJobStatus.TransferState(13128, 131072, 10, 4096, 30)
        )
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_queue_and_jobs_2(self):
        """Queued items, parallel jobs running, multiple files, multiple chunks"""
        output = """
        [0] queue (sftp://someone:@localhost)  -- 15.6 KiB/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp/remote/a /tmp/test_lftp/local/ -- 152k/26M (0%) 3.9 KiB/s
                -[2] mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/ -- 350k/394k (88%) 11.7 KiB/s
        Commands queued:
         1. mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/
         2. mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/
        [1] mirror -c /tmp/test_lftp/remote/a /tmp/test_lftp/local/  -- 152k/26M (0%) 3.9 KiB/s
        \\transfer `ab'
        `ab', got 126558 of 25165824 (0%) 3.9K/s eta:1h45m
        \chunk 0-6291456
        `ab' at 32115 (0%) 1006b/s eta:1h43m [Receiving data]
        \chunk 18874368-25165823
        `ab' at 18906710 (0%) 1007b/s eta:1h43m [Receiving data]
        \chunk 12582912-18874367
        `ab' at 12614060 (0%) 998b/s eta:1h45m [Receiving data]
        \chunk 6291456-12582911
        `ab' at 6322409 (0%) 998b/s eta:1h45m [Receiving data]
        [2] mirror -c /tmp/test_lftp/remote/b /tmp/test_lftp/local/  -- 350k/394k (88%) 11.7 KiB/s
        \\transfer `bb'
        `bb', got 124150 of 131072 (94%) 3.9K/s eta:2s
        \chunk 0-32768
        `bb' at 30932 (23%) 997b/s eta:2s [Receiving data]
        \chunk 98304-131071
        `bb' at 129447 (95%) 998b/s eta:2s [Receiving data]
        \chunk 65536-98303
        `bb' at 96690 (95%) 998b/s eta:2s [Receiving data]
        \chunk 32768-65535
        `bb' at 63689 (94%) 997b/s eta:2s [Receiving data]
        \mirror `ba'  -- 225k/263k (85%) 7.8 KiB/s
        \\transfer `ba/baa'
        `baa', got 123531 of 131072 (94%) 3.9K/s eta:2s
        \chunk 0-32768
        `baa' at 30944 (23%) 998b/s eta:2s [Receiving data]
        \chunk 98304-131071
        `baa' at 129234 (94%) 997b/s eta:2s [Receiving data]
        \chunk 65536-98303
        `baa' at 96253 (93%) 998b/s eta:2s [Receiving data]
        \chunk 32768-65535
        `baa' at 63708 (94%) 997b/s eta:2s [Receiving data]
        \\transfer `ba/bab'
        `bab', got 101391 of 131072 (77%) 3.9K/s eta:26s
        \chunk 0-32768
        `bab' at 31890 (24%) 1003b/s eta:1s [Receiving data]
        \chunk 98304-131071
        `bab' at 129233 (94%) 997b/s eta:2s [Receiving data]
        \chunk 65536-98303
        `bab' at 96253 (93%) 997b/s eta:2s [Receiving data]
        \chunk 32768-65535
        `bab' at 40623 (23%) 960b/s eta:26s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(152*1024, 26*1024*1024, 0, 3993, None)
        golden_job1.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(126558, 25165824, 0, 3993, 1*3600+45*60)
        )
        golden_job2 = LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="b",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(350*1024, 394*1024, 88, 11980, None)
        golden_job2.add_active_file_transfer_state(
            "bb", LftpJobStatus.TransferState(124150, 131072, 94, 3993, 2)
        )
        golden_job2.add_active_file_transfer_state(
            "ba/baa", LftpJobStatus.TransferState(123531, 131072, 94, 3993, 2)
        )
        golden_job2.add_active_file_transfer_state(
            "ba/bab", LftpJobStatus.TransferState(101391, 131072, 77, 3993, 26)
        )
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_1(self):
        """1 job, 1 file, no chunks"""
        output = """
        [0] queue (sftp://someone:@localhost)
        sftp://someone:@localhost/home/someone
        Now executing: [1] pget -c /tmp/test_lftp/remote/c -o /tmp/test_lftp/local/
        [1] pget -c /tmp/test_lftp/remote/c -o /tmp/test_lftp/local/
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp/remote/c' at 4585 (3%) 1.2K/s eta:2m [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="c",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(4585, None, 3, 1228, 2*60)
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_quotes(self):
        output = """
        [0] queue (sftp://someone:@localhost)
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp/remote/e e /tmp/test_lftp/local/ -- 0/132k (0%)
                -[2] pget -c /tmp/test_lftp/remote/d d -o /tmp/test_lftp/local/
        [1] mirror -c /tmp/test_lftp/remote/e e /tmp/test_lftp/local/  -- 0/132k (0%)
        \\transfer `e e a'
        `e e a' at 11804 (9%) 1003b/s eta:2m [Receiving data]
        [2] pget -c /tmp/test_lftp/remote/d d -o /tmp/test_lftp/local/
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp/remote/d d' at 11982 (9%) 998b/s eta:2m [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="e e",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(0, 132*1024, 0, None, None)
        golden_job1.add_active_file_transfer_state(
            "e e a", LftpJobStatus.TransferState(11804, None, 9, 1003, 2*60)
        )
        golden_job2 = LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="d d",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(11982, None, 9, 998, 2*60)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_getting_file_list(self):
        output = """
        [0] queue (sftp://someone:@localhost)
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp/remote/e e /tmp/test_lftp/local/
                -[2] pget -c /tmp/test_lftp/remote/d d -o /tmp/test_lftp/local/
        [1] mirror -c /tmp/test_lftp/remote/e e /tmp/test_lftp/local/
        Getting file list (25) [Receiving data]
        [2] pget -c /tmp/test_lftp/remote/d d -o /tmp/test_lftp/local/
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp/remote/d d' at 23 (0%) [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="e e",
                                    flags="-c")
        golden_job2 = LftpJobStatus(job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="d d",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(23, None, 0, None, None)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)
