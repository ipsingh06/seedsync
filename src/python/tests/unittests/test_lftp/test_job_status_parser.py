# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest

from lftp import LftpJobStatusParser, LftpJobStatus, LftpJobStatusParserError


# noinspection PyPep8
class TestLftpJobStatusParser(unittest.TestCase):
    def setUp(self):
        # Show full diff
        self.maxDiff = None

    def test_size_to_bytes(self):
        self.assertEqual(345, LftpJobStatusParser._size_to_bytes("345"))
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

    def test_empty_output_4(self):
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost/home/someone
        [0] Done (queue (sftp://someone:@localhost))
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
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="a",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="c",
                          flags="-c"),
            LftpJobStatus(job_id=3,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_id=4,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_id=5,
                          job_type=LftpJobStatus.Type.MIRROR,
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
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b s s",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="a s s",
                          flags="-c"),
            LftpJobStatus(job_id=3,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b s s",
                          flags="-c"),
            LftpJobStatus(job_id=4,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="a s s",
                          flags="-c"),
            LftpJobStatus(job_id=5,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_id=6,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="a",
                          flags="-c"),
            LftpJobStatus(job_id=7,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_id=8,
                          job_type=LftpJobStatus.Type.PGET,
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
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="c",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_id=3,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(17*1024, 26*1024*1024, 0, 5*1024, None)
        golden_job1.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(None, None, None, 997, 22)
        )
        golden_job1.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(13733, 25165824, 0, 4*1024, 1*3600+45*60)
        )
        golden_job2 = LftpJobStatus(job_id=3,
                                    job_type=LftpJobStatus.Type.MIRROR,
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
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(152*1024, 26*1024*1024, 0, 3993, None)
        golden_job1.add_active_file_transfer_state(
            "ab", LftpJobStatus.TransferState(126558, 25165824, 0, 3993, 1*3600+45*60)
        )
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
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

    def test_queue_and_jobs_3(self):
        """Queued items, parallel jobs running, 'cd' line in queued pget"""
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_n_l73hx8/remote/a /tmp/test_lftp_n_l73hx8/local/
        -[2] pget -c /tmp/test_lftp_n_l73hx8/remote/d d -o /tmp/test_lftp_n_l73hx8/local/
        Commands queued:
        1.  mirror -c "/tmp/test_lftp_n_l73hx8/remote/b"  "/tmp/test_lftp_n_l73hx8/local/" 
        2.  pget -c "/tmp/test_lftp_n_l73hx8/remote/c" -o "/tmp/test_lftp_n_l73hx8/local/" 
        cd /home/someone
        3.  mirror -c "/tmp/test_lftp_n_l73hx8/remote/e e"  "/tmp/test_lftp_n_l73hx8/local/" 
        [1] mirror -c /tmp/test_lftp_n_l73hx8/remote/a /tmp/test_lftp_n_l73hx8/local/ 
        Getting file list (10) [Receiving data]
        [2] pget -c /tmp/test_lftp_n_l73hx8/remote/d d -o /tmp/test_lftp_n_l73hx8/local/ 
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp_n_l73hx8/remote/d d' at 10 (0%) [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="b",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="c",
                          flags="-c"),
            LftpJobStatus(job_id=3,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="e e",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="d d",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, None, None)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_queue_and_jobs_4(self):
        """Queued items, parallel jobs running, '\mirror' line with 'Getting file list'"""
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_controller_zph2s53/remote/ra /tmp/test_controller_zph2s53/local/ -- 0/1.1k (0%)
        -[2] mirror -c /tmp/test_controller_zph2s53/remote/rb /tmp/test_controller_zph2s53/local/ -- 20/9.3k (0%)
        Commands queued:
        1.  pget -c "/tmp/test_controller_zph2s53/remote/rc" -o "/tmp/test_controller_zph2s53/local/" 
        [1] mirror -c /tmp/test_controller_zph2s53/remote/ra /tmp/test_controller_zph2s53/local/  -- 0/1.1k (0%)
        \\transfer `raa' 
        `raa' at 0 (0%) [Connecting...]
        \mirror `rab' 
        rab: Getting file list (27) [Receiving data]
        [2] mirror -c /tmp/test_controller_zph2s53/remote/rb /tmp/test_controller_zph2s53/local/  -- 20/9.3k (0%)
        \\transfer `rba' 
        `rba' at 0 (0%) [Connecting...]
        \\transfer `rbb' 
        `rbb' at 0 (0%) [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="rc",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="ra",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(0, 1126, 0, None, None)
        golden_job1.add_active_file_transfer_state("raa", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="rb",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(20, 9523, 0, None, None)
        golden_job2.add_active_file_transfer_state("rba", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_job2.add_active_file_transfer_state("rbb", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_queue_and_jobs_5(self):
        """Queued items, parallel jobs running, '\mirror' line with 'cd'"""
        # noinspection PyPep8
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_controllerw0sbqxe_/remote/ra /tmp/test_controllerw0sbqxe_/local/ -- 0/1.1k (0%)
        -[2] mirror -c /tmp/test_controllerw0sbqxe_/remote/rb /tmp/test_controllerw0sbqxe_/local/ -- 49/9.3k (0%)
        Commands queued:
        1.  pget -c "/tmp/test_controllerw0sbqxe_/remote/rc" -o "/tmp/test_controllerw0sbqxe_/local/" 
        [1] mirror -c /tmp/test_controllerw0sbqxe_/remote/ra /tmp/test_controllerw0sbqxe_/local/  -- 0/1.1k (0%)
        \\transfer `raa' 
        `raa' at 0 (0%) [Connecting...]
        \mirror `rab' 
        cd `/tmp/test_controllerw0sbqxe_/remote/ra/rab' [Connecting...]
        [2] mirror -c /tmp/test_controllerw0sbqxe_/remote/rb /tmp/test_controllerw0sbqxe_/local/  -- 49/9.3k (0%)
        \\transfer `rba' 
        `rba' at 0 (0%) [Receiving data]
        \\transfer `rbb' 
        `rbb' at 0 (0%) [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="rc",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="ra",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(0, 1126, 0, None, None)
        golden_job1.add_active_file_transfer_state("raa", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="rb",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(49, 9523, 0, None, None)
        golden_job2.add_active_file_transfer_state("rba", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_job2.add_active_file_transfer_state("rbb", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_queue_and_jobs_6(self):
        """Queued items, parallel jobs running, '\mirror' line with no units for local_size"""
        output = """
        [0] queue (sftp://someone:@localhost)  -- 252 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_controllerbsn4wlu2/remote/ra /tmp/test_controllerbsn4wlu2/local/ -- 249/8.2k (3%) 100 B/s
        -[2] mirror -c /tmp/test_controllerbsn4wlu2/remote/rb /tmp/test_controllerbsn4wlu2/local/ -- 374/9.3k (4%) 153 B/s
        Commands queued:
        1.  pget -c "/tmp/test_controllerbsn4wlu2/remote/rc" -o "/tmp/test_controllerbsn4wlu2/local/" 
        [1] mirror -c /tmp/test_controllerbsn4wlu2/remote/ra /tmp/test_controllerbsn4wlu2/local/  -- 249/8.2k (3%) 100 B/s
        \\transfer `raa' 
        `raa' at 238 (23%) 100b/s eta:8s [Receiving data]
        \mirror `rab'  -- 0/7.2k (0%)
        \\transfer `rab/raba' 
        `raba' at 0 (0%) [Connecting...]
        \\transfer `rab/rabb' 
        `rabb' at 0 (0%) [Waiting for response...]
        [2] mirror -c /tmp/test_controllerbsn4wlu2/remote/rb /tmp/test_controllerbsn4wlu2/local/  -- 374/9.3k (4%) 153 B/s
        \\transfer `rba' 
        `rba' at 159 (3%) 77b/s eta:51s [Receiving data]
        \\transfer `rbb' 
        `rbb' at 153 (2%) 76b/s eta:66s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="rc",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="ra",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(249, 8396, 3, 100, None)
        golden_job1.add_active_file_transfer_state("raa", LftpJobStatus.TransferState(None, None, None, 100, 8))
        golden_job1.add_active_file_transfer_state("rab/raba", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_job1.add_active_file_transfer_state("rab/rabb", LftpJobStatus.TransferState(None, None, None, None, None))
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="rb",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(374, 9523, 4, 153, None)
        golden_job2.add_active_file_transfer_state("rba", LftpJobStatus.TransferState(None, None, None, 77, 51))
        golden_job2.add_active_file_transfer_state("rbb", LftpJobStatus.TransferState(None, None, None, 76, 66))
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
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="c",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(None, None, None, 1228, 2*60)
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_2(self):
        """1 job, 1 dir, no units in local size"""
        output = """
        [0] queue (sftp://someone:@localhost)  -- 90 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_rm_s6oau/remote/a /tmp/test_lftp_rm_s6oau/local/ -- 345/26M (0%) 90 B/s
        [1] mirror -c /tmp/test_lftp_rm_s6oau/remote/a /tmp/test_lftp_rm_s6oau/local/  -- 345/26M (0%) 90 B/s
        \\transfer `aa' 
        `aa' at 315 (1%) 90b/s eta:4m [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(345, 26*1024*1024, 0, 90, None)
        golden_job1.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(None, None, None, 90, 4*60)
        )
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_3(self):
        """1 job, 1 file, chunks"""
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost/home/someone
        Now executing: [1] pget -c /tmp/test_lftp/remote/A.b.C.rar -o /tmp/lftp/
        [1] pget -c /tmp/test_lftp/remote/A.b.C.rar -o /tmp/lftp/ 
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp/remote/A.b.C.rar', got 2622559389 of 3274103236 (80%) 
        \chunk 0-2752841944
        `/tmp/test_lftp/remote/A.b.C.rar' at 2622559389 (0%) [Receiving data]
        \chunk 3143787913-3274103235 
        `/tmp/test_lftp/remote/A.b.C.rar' at 3143787913 (0%) [Connecting...]
        \chunk 3013472590-3143787912 
        `/tmp/test_lftp/remote/A.b.C.rar' at 3013472590 (0%) [Connecting...]
        \chunk 2883157267-3013472589 
        `/tmp/test_lftp/remote/A.b.C.rar' at 2883157267 (0%) [Connecting...]
        \chunk 2752841944-2883157266 
        `/tmp/test_lftp/remote/A.b.C.rar' at 2752841944 (0%) [Connecting...]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="A.b.C.rar",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(2622559389, 3274103236, 80, None, None)
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
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="e e",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(0, 132*1024, 0, None, None)
        golden_job1.add_active_file_transfer_state(
            "e e a", LftpJobStatus.TransferState(None, None, None, 1003, 2*60)
        )
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="d d",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, 998, 2*60)
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
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="e e",
                                    flags="-c")
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="d d",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, None, None)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_mirror_empty(self):
        # '-o' in filename
        output = """
        [0] queue (sftp://someone:@localhost)  -- 59 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [2] mirror -c /tmp/test_lftp_1d7axxcf/remote/a /tmp/test_lftp_1d7axxcf/local/ -- 100/100 (100%) 59 B/s
        [2] mirror -c /tmp/test_lftp_1d7axxcf/remote/a /tmp/test_lftp_1d7axxcf/local/  -- 100/100 (100%) 59 B/s
        \\transfer `aa' 
        `aa' at 59 (59%)
        \\mirror `Sample' 
        Sample: 
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(100, 100, 100, 59, None)
        golden_job1.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_mirror_mkdir(self):
        output = """        
        [0] queue (sftp://someone:@localhost:22) 
        sftp://someone:@localhost:22/home/someone
        Now executing: [1] mirror -c /tmp/test_controllerxnx7xw6x/remote/ra /tmp/test_controllerxnx7xw6x/local/ -- 0/1.1k (0%)
        [1] mirror -c /tmp/test_controllerxnx7xw6x/remote/ra /tmp/test_controllerxnx7xw6x/local/  -- 0/1.1k (0%)
        \\transfer `raa' 
        `raa' at 0 (0%) [Connecting...]
        \mirror `rab' 
        mkdir `/tmp/test_controllerxnx7xw6x/local/ra/rab' []
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="ra",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(0, 1126, 0, None, None)
        golden_job1.add_active_file_transfer_state(
            "raa", LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_connecting(self):
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost
        Now executing: [1] pget -c /tmp/test_lftp_jsecvi6m/remote/c -o /tmp/test_lftp_jsecvi6m/local/
        [1] pget -c /tmp/test_lftp_jsecvi6m/remote/c -o /tmp/test_lftp_jsecvi6m/local/ 
        sftp://someone:@localhost
        `/tmp/test_lftp_jsecvi6m/remote/c' at 0 [Connecting...]
        [2] mirror -c /tmp/test_lftp_yb58ogg6/remote/a /tmp/test_lftp_yb58ogg6/local/ 
        cd `/tmp/test_lftp_yb58ogg6/remote/a' [Connecting...]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="c",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(None, None, None, None, None)
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_almost_done(self):
        """Almost done job has a special shorter 'at' line for child file"""
        output = """
        [0] queue (sftp://someone:@localhost)  -- 98 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [3] mirror -c /tmp/test_lftp_sbz92f__/remote/c'c'c'c /tmp/test_lftp_sbz92f__/local/ -- 100/100 (100%) 98 B/s
        [3] mirror -c /tmp/test_lftp_sbz92f__/remote/c'c'c'c /tmp/test_lftp_sbz92f__/local/  -- 100/100 (100%) 98 B/s
        \\transfer `c'''c.txt' 
        `c'''c.txt' at 100 (100%)
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=3,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="c'c'c'c",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(100, 100, 100, 98, None)
        golden_job1.add_active_file_transfer_state(
            "c'''c.txt", LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_empty(self):
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost
        Now executing: [2] mirror -c /tmp/test_lftp_yb58ogg6/remote/a /tmp/test_lftp_yb58ogg6/local/
        [2] mirror -c /tmp/test_lftp_yb58ogg6/remote/a /tmp/test_lftp_yb58ogg6/local/ 
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_jobs = [golden_job2]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_with_done_line(self):
        output = """
        [0] queue (sftp://someone:@localhost)  -- 59 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [2] mirror -c /tmp/test_lftp_1d7axxcf/remote/a /tmp/test_lftp_1d7axxcf/local/ -- 100/100 (100%) 59 B/s
        [2] mirror -c /tmp/test_lftp_1d7axxcf/remote/a /tmp/test_lftp_1d7axxcf/local/  -- 100/100 (100%) 59 B/s
        \\transfer `aa' 
        `aa' at 59 (59%) 
        [0] Done (queue (sftp://someone:@localhost))
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(100, 100, 100, 59, None)
        golden_job1.add_active_file_transfer_state(
            "aa", LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_missing_pget_data_line(self):
        output = """
        [0] queue (sftp://seedsynctest:@localhost:22) 
        sftp://seedsynctest:@localhost:22/home/seedsynctest
        Now executing: [3] mirror -c /tmp/test_lftp_ns99k0im/remote/c -o c /tmp/test_lftp_ns99k0im/local/
        -[4] pget -c /tmp/test_lftp_ns99k0im/remote/d -o d.txt -o /tmp/test_lftp_ns99k0im/local/
        [3] mirror -c /tmp/test_lftp_ns99k0im/remote/c -o c /tmp/test_lftp_ns99k0im/local/ 
        Getting file list (162) [Receiving data]
        [4] pget -c /tmp/test_lftp_ns99k0im/remote/d -o d.txt -o /tmp/test_lftp_ns99k0im/local/ 
        sftp://seedsynctest:@localhost:22/home/seedsynctest
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=3,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="c -o c",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(None, None, None, None, None)
        golden_job2 = LftpJobStatus(job_id=4,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="d -o d.txt",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, None, None)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_raises_error_on_bad_status(self):
        output = """
        [0] queue (sftp://someone:@localhost) 
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_controllerw0sbqxe_/remote/ra /tmp/test_controllerw0sbqxe_/local/ -- 0/1.1k (0%)
        -[2] mirror -c /tmp/test_controllerw0sbqxe_/remote/rb /tmp/test_controllerw0sbqxe_/local/ -- 49/9.3k (0%)
        Commands queued:
        1.  pget -c "/tmp/test_controllerw0sbqxe_/remote/rc" -o "/tmp/test_controllerw0sbqxe_/local/" 
        bad string uh oh
        """
        parser = LftpJobStatusParser()
        with self.assertRaises(LftpJobStatusParserError):
            parser.parse(output)

    def test_jobs_special_char_1(self):
        # Apostrophe/single quote
        output = """
        [0] queue (sftp://someone:@localhost)  -- 18 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_g6z3_el7/remote/aaa'aaa /tmp/test_lftp_g6z3_el7/local/ -- 36/128 (28%) 18 B/s
        -[2] pget -c /tmp/test_lftp_g6z3_el7/remote/b''b''b.txt -o /tmp/test_lftp_g6z3_el7/local/
        Commands queued:
        1.  mirror -c "/tmp/test_lftp_g6z3_el7/remote/c'c'c'c"  "/tmp/test_lftp_g6z3_el7/local/" 
        2.  pget -c "/tmp/test_lftp_g6z3_el7/remote/d'''d.txt" -o "/tmp/test_lftp_g6z3_el7/local/" 
        [1] mirror -c /tmp/test_lftp_g6z3_el7/remote/aaa'aaa /tmp/test_lftp_g6z3_el7/local/  -- 36/128 (28%) 18 B/s
        \\transfer `aa'aa'aa.txt' 
        `aa'aa'aa.txt' at 21 (16%) [Receiving data]
        [2] pget -c /tmp/test_lftp_g6z3_el7/remote/b''b''b.txt -o /tmp/test_lftp_g6z3_el7/local/ 
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp_g6z3_el7/remote/b''b''b.txt' at 210 (82%) 94b/s eta:0s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="c'c'c'c",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="d'''d.txt",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="aaa'aaa",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(36, 128, 28, 18, None)
        golden_job1.add_active_file_transfer_state(
            "aa'aa'aa.txt", LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="b''b''b.txt",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, 94, 0)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_special_char_2(self):
        # Double quote
        output = """
        [0] queue (sftp://someone:@localhost)  -- 12 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_w8d2q1ot/remote/aaa"aaa /tmp/test_lftp_w8d2q1ot/local/ -- 19/128 (14%) 12 B/s
        -[2] pget -c /tmp/test_lftp_w8d2q1ot/remote/b""b""b.txt -o /tmp/test_lftp_w8d2q1ot/local/
        Commands queued:
        1.  mirror -c "/tmp/test_lftp_w8d2q1ot/remote/c\"c\"c\"c"  "/tmp/test_lftp_w8d2q1ot/local/" 
        2.  pget -c "/tmp/test_lftp_w8d2q1ot/remote/d\"\"\"d.txt" -o "/tmp/test_lftp_w8d2q1ot/local/" 
        [1] mirror -c /tmp/test_lftp_w8d2q1ot/remote/aaa"aaa /tmp/test_lftp_w8d2q1ot/local/  -- 19/128 (14%) 12 B/s
        \\transfer `aa"aa"aa.txt' 
        `aa"aa"aa.txt' at 16 (12%) [Receiving data]
        [2] pget -c /tmp/test_lftp_w8d2q1ot/remote/b""b""b.txt -o /tmp/test_lftp_w8d2q1ot/local/ 
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp_w8d2q1ot/remote/b""b""b.txt' at 203 (79%) 29b/s eta:2s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="c\"c\"c\"c",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="d\"\"\"d.txt",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="aaa\"aaa",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(19, 128, 14, 12, None)
        golden_job1.add_active_file_transfer_state(
            "aa\"aa\"aa.txt", LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="b\"\"b\"\"b.txt",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, 29, 2)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_special_char_3(self):
        # Mix of single quotes, double quotes and spaces
        output = """
        [0] queue (sftp://someone:@localhost)  -- 15 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_m9mxjip7/remote/a' aa"aaa /tmp/test_lftp_m9mxjip7/local/ -- 48/128 (37%) 15 B/s
        -[2] pget -c /tmp/test_lftp_m9mxjip7/remote/"b ' "b" ' "b.txt -o /tmp/test_lftp_m9mxjip7/local/
        Commands queued:
        1.  mirror -c "/tmp/test_lftp_m9mxjip7/remote/'c\" c \" 'c' \"c\""  "/tmp/test_lftp_m9mxjip7/local/" 
        2.  pget -c "/tmp/test_lftp_m9mxjip7/remote/'d\" ' \" ' \"d.txt" -o "/tmp/test_lftp_m9mxjip7/local/" 
        [1] mirror -c /tmp/test_lftp_m9mxjip7/remote/a' aa"aaa /tmp/test_lftp_m9mxjip7/local/  -- 48/128 (37%) 15 B/s
        \\transfer `aa"a ' a"aa.txt' 
        `aa"a ' a"aa.txt' at 43 (33%) 15b/s eta:6s [Receiving data]
        [2] pget -c /tmp/test_lftp_m9mxjip7/remote/"b ' "b" ' "b.txt -o /tmp/test_lftp_m9mxjip7/local/ 
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp_m9mxjip7/remote/"b ' "b" ' "b.txt' at 236 (92%) 26b/s eta:1s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="'c\" c \" 'c' \"c\"",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="'d\" ' \" ' \"d.txt",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a' aa\"aaa",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(48, 128, 37, 15, None)
        golden_job1.add_active_file_transfer_state(
            "aa\"a ' a\"aa.txt", LftpJobStatus.TransferState(None, None, None, 15, 6)
        )
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="\"b ' \"b\" ' \"b.txt",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, 26, 1)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_special_char_4(self):
        # '-o' in filename
        output = """
        [0] queue (sftp://someone:@localhost)  -- 16 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_xi6gkbhv/remote/a -o a /tmp/test_lftp_xi6gkbhv/local/ -- 60/128 (46%) 16 B/s
        -[2] pget -c /tmp/test_lftp_xi6gkbhv/remote/b -o b.txt -o /tmp/test_lftp_xi6gkbhv/local/
        Commands queued:
        1.  mirror -c "/tmp/test_lftp_xi6gkbhv/remote/c -o c"  "/tmp/test_lftp_xi6gkbhv/local/" 
        2.  pget -c "/tmp/test_lftp_xi6gkbhv/remote/d -o d.txt" -o "/tmp/test_lftp_xi6gkbhv/local/" 
        [1] mirror -c /tmp/test_lftp_xi6gkbhv/remote/a -o a /tmp/test_lftp_xi6gkbhv/local/  -- 60/128 (46%) 16 B/s
        \\transfer `a -o a.txt' 
        `a -o a.txt' at 55 (42%) 16b/s eta:4s [Receiving data]
        [2] pget -c /tmp/test_lftp_xi6gkbhv/remote/b -o b.txt -o /tmp/test_lftp_xi6gkbhv/local/ 
        sftp://someone:@localhost/home/someone
        `/tmp/test_lftp_xi6gkbhv/remote/b -o b.txt' at 240 (93%) 26b/s eta:1s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_queue = [
            LftpJobStatus(job_id=1,
                          job_type=LftpJobStatus.Type.MIRROR,
                          state=LftpJobStatus.State.QUEUED,
                          name="c -o c",
                          flags="-c"),
            LftpJobStatus(job_id=2,
                          job_type=LftpJobStatus.Type.PGET,
                          state=LftpJobStatus.State.QUEUED,
                          name="d -o d.txt",
                          flags="-c"),
        ]
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a -o a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(60, 128, 46, 16, None)
        golden_job1.add_active_file_transfer_state(
            "a -o a.txt", LftpJobStatus.TransferState(None, None, None, 16, 4)
        )
        golden_job2 = LftpJobStatus(job_id=2,
                                    job_type=LftpJobStatus.Type.PGET,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="b -o b.txt",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(None, None, None, 26, 1)
        golden_jobs = [golden_job1, golden_job2]
        self.assertEqual(len(golden_queue)+len(golden_jobs), len(statuses))
        statuses_queue = [j for j in statuses if j.state == LftpJobStatus.State.QUEUED]
        self.assertEqual(golden_queue, statuses_queue)
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_jobs_chmod(self):
        output = """
        [0] queue (sftp://someone:@localhost:22)  -- 12.26 MiB/s
        sftp://someone:@localhost:22/remote/path
        Now executing: [3] mirror -c /remote/path/Space.Trek.S23E03.720p /local/path/ -- 985M/985M (100%)
            -[4] mirror -c /remote/path/Star.Battle.Movie /local/path/ -- 116M/1.2G (9%) 12.26 MiB/s
        [3] mirror -c /remote/path/Space.Trek.S23E03.720p /local/path/  -- 985M/985M (100%)
        chmod Space.Trek.S23E03.720p.r06 
        file:/local/path/Space.Trek.S23E03.720p
        `Space.Trek.S23E03.720p.r06' []
        chmod Space.Trek.S23E03.720p.r07 
        file:/local/path/Space.Trek.S23E03.720p
        `Space.Trek.S23E03.720p.r07' []
        chmod Space.Trek.S23E03.720p.r08 
        file:/local/path/Space.Trek.S23E03.720p
        `Space.Trek.S23E03.720p.r08' []
        chmod Space.Trek.S23E03.720p.r09 
        file:/local/path/Space.Trek.S23E03.720p
        `Space.Trek.S23E03.720p.r09' []
        [4] mirror -c /remote/path/Star.Battle.Movie /local/path/  -- 116M/1.2G (9%) 12.26 MiB/s
        \\transfer `star.battle.movie.720p.r07' 
        `star.battle.movie.720p.r07', got 44628032 of 50000000 (89%) 1.10M/s eta:5s 
        \chunk 9011200-25000000
        `star.battle.movie.720p.r07' at 19628032 (25%) 1.10M/s eta:5s [Receiving data]
        \\transfer `star.battle.movie.720p.r08' 
        `star.battle.movie.720p.r08', got 15237120 of 50000000 (30%) 2.04M/s 
        \chunk 0-25000000
        `star.battle.movie.720p.r08' at 13664256 (27%) 1.36M/s eta:8s [Receiving data]
        \chunk 37500000-49999999 
        `star.battle.movie.720p.r08' at 38581344 (8%) 696.2K/s eta:16s [Receiving data]
        \chunk 25000000-37499999 
        `star.battle.movie.720p.r08' at 25491520 (3%) [Receiving data]
        \\transfer `star.battle.movie.720p.r09' 
        `star.battle.movie.720p.r09', got 21692416 of 50000000 (43%) 4.05M/s eta:16s 
        \chunk 0-12500000
        `star.battle.movie.720p.r09' at 12419072 (24%) 1.28M/s eta:0s [Receiving data]
        \chunk 37500000-49999999 
        `star.battle.movie.720p.r09' at 38843488 (10%) 662.8K/s eta:16s [Receiving data]
        \chunk 25000000-37499999 
        `star.battle.movie.720p.r09' at 28047424 (24%) 963.8K/s eta:10s [Receiving data]
        \chunk 12500000-24999999 
        `star.battle.movie.720p.r09' at 17382432 (39%) 1.19M/s eta:6s [Receiving data]
        \\transfer `star.battle.movie.720p.r10' 
        `star.battle.movie.720p.r10', got 33930272 of 50000000 (67%) 5.06M/s eta:6s 
        \chunk 37500000-49999999 
        `star.battle.movie.720p.r10' at 43037792 (44%) 1.16M/s eta:6s [Receiving data]
        \chunk 25000000-37499999 
        `star.battle.movie.720p.r10' at 32503872 (60%) 1.19M/s eta:4s [Receiving data]
        \chunk 12500000-24999999 
        `star.battle.movie.720p.r10' at 20888608 (67%) 1.33M/s eta:3s [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)

        golden_job1 = LftpJobStatus(job_id=3,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="Space.Trek.S23E03.720p",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(1032847360, 1032847360, 100, None, None)

        golden_job2 = LftpJobStatus(job_id=4,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="Star.Battle.Movie",
                                    flags="-c")
        golden_job2.total_transfer_state = LftpJobStatus.TransferState(121634816, 1288490188, 9, 12855541, None)
        golden_job2.add_active_file_transfer_state(
            "star.battle.movie.720p.r07",
            LftpJobStatus.TransferState(44628032, 50000000, 89, 1153433, 5)
        )
        golden_job2.add_active_file_transfer_state(
            "star.battle.movie.720p.r08",
            LftpJobStatus.TransferState(15237120, 50000000, 30, 2139095, None)
        )
        golden_job2.add_active_file_transfer_state(
            "star.battle.movie.720p.r09",
            LftpJobStatus.TransferState(21692416, 50000000, 43, 4246732, 16)
        )
        golden_job2.add_active_file_transfer_state(
            "star.battle.movie.720p.r10",
            LftpJobStatus.TransferState(33930272, 50000000, 67, 5305794, 6)
        )

        self.assertEqual(2, len(statuses))
        self.assertEqual(golden_job1, statuses[0])
        self.assertEqual(golden_job2, statuses[1])

    def test_jobs_chmod_two_liner(self):
        output = """
        [0] queue (sftp://someone:@localhost:22)  -- 1.8 KiB/s
        sftp://someone:@localhost:22/remote/path
        Now executing: [1] mirror -c /remote/path/Space.Trek /local/path/ -- 3.1k/617M (0%) 1.8 KiB/s
        [1] mirror -c /remote/path/Space.Trek /local/path/  -- 3.1k/617M (0%) 1.8 KiB/s
        \mirror `Space.Trek.S08E04' 
        chmod Space.Trek.S08E04.sfv 
            file:/local/path/Space.Trek/Space.Trek.S08E04
        \mirror `Space.Trek.S08E05'  -- 605/51M (0%)
        \\transfer `Space.Trek.S08E05/space.trek.s08e05.r06' 
            `space.trek.s08e05.r06' at 0 (0%) [Waiting for response...]
        \mirror `Space.Trek.S08E06'  -- 1.6k/517M (0%) 932 B/s
        \\transfer `Space.Trek.S08E06/space.trek.s08e06.nfo' 
            `space.trek.s08e06.nfo' at 932 (100%) [Receiving data]
        \mirror `Space.Trek.S08E07'  -- 932/51M (0%) 932 B/s
        \\transfer `Space.Trek.S08E07/space.trek.s08e07.nfo' 
        `space.trek.s08e07.nfo' at 932 (100%) [Receiving data]
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)

        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="Space.Trek",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(3174, 646971392, 0, 1843, None)
        golden_job1.add_active_file_transfer_state(
            "Space.Trek.S08E05/space.trek.s08e05.r06",
            LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_job1.add_active_file_transfer_state(
            "Space.Trek.S08E06/space.trek.s08e06.nfo",
            LftpJobStatus.TransferState(None, None, None, None, None)
        )
        golden_job1.add_active_file_transfer_state(
            "Space.Trek.S08E07/space.trek.s08e07.nfo",
            LftpJobStatus.TransferState(None, None, None, None, None)
        )
        self.assertEqual(1, len(statuses))
        self.assertEqual(golden_job1, statuses[0])

    def test_removes_jobs_command(self):
        output = """
        jobs -v
        [0] queue (sftp://someone:@localhost)  -- 90 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_rm_s6oau/remote/a /tmp/test_lftp_rm_s6oau/local/ -- 345/26M (0%) 90 B/s
        [1] mirror -c /tmp/test_lftp_rm_s6oau/remote/a /tmp/test_lftp_rm_s6oau/local/  -- 345/26M (0%) 90 B/s
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(345, 26*1024*1024, 0, 90, None)
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)

    def test_removes_log_line(self):
        output = """
        2020-06-09 04:25:46 sftp://user@example.com:22/path/on/server/file.nfo -> /path/on/local/file.nfo 0-1400 2.8 KiB/s
        [0] queue (sftp://someone:@localhost)  -- 90 B/s
        sftp://someone:@localhost/home/someone
        Now executing: [1] mirror -c /tmp/test_lftp_rm_s6oau/remote/a /tmp/test_lftp_rm_s6oau/local/ -- 345/26M (0%) 90 B/s
        [1] mirror -c /tmp/test_lftp_rm_s6oau/remote/a /tmp/test_lftp_rm_s6oau/local/  -- 345/26M (0%) 90 B/s
        """
        parser = LftpJobStatusParser()
        statuses = parser.parse(output)
        golden_job1 = LftpJobStatus(job_id=1,
                                    job_type=LftpJobStatus.Type.MIRROR,
                                    state=LftpJobStatus.State.RUNNING,
                                    name="a",
                                    flags="-c")
        golden_job1.total_transfer_state = LftpJobStatus.TransferState(345, 26*1024*1024, 0, 90, None)
        golden_jobs = [golden_job1]
        self.assertEqual(len(golden_jobs), len(statuses))
        statuses_jobs = [j for j in statuses if j.state == LftpJobStatus.State.RUNNING]
        self.assertEqual(golden_jobs, statuses_jobs)
