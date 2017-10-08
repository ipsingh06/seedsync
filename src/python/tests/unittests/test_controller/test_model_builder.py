# Copyright 2017, Inderpreet Singh, All rights reserved.

import logging
import sys
import unittest

from system import SystemFile
from lftp import LftpJobStatus
from model import ModelError, ModelFile, Model
from controller import ModelBuilder


class TestModelBuilder(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger(TestModelBuilder.__name__)
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        self.model_builder = ModelBuilder()
        self.model_builder.set_base_logger(logger)

    def __build_test_model_children_tree_1(self) -> Model:
        """Build a test model for children testing"""
        self.model_builder.clear()

        r_a = SystemFile("a", 1024, True)
        r_aa = SystemFile("aa", 512, False)
        r_a.add_child(r_aa)
        r_ab = SystemFile("ab", 512, False)
        r_a.add_child(r_ab)
        r_b = SystemFile("b", 3090, True)
        r_ba = SystemFile("ba", 2048, True)
        r_b.add_child(r_ba)
        r_baa = SystemFile("baa", 2048, False)
        r_ba.add_child(r_baa)
        r_bb = SystemFile("bb", 42, True)  # only in remote
        r_b.add_child(r_bb)
        r_bba = SystemFile("bba", 42, False)  # only in remote
        r_bb.add_child(r_bba)
        r_bd = SystemFile("bd", 1000, False)
        r_b.add_child(r_bd)
        r_c = SystemFile("c", 1234, False)  # only in remote
        r_d = SystemFile("d", 5678, True)  # only in remote
        r_da = SystemFile("da", 5678, False)  # only in remote
        r_d.add_child(r_da)

        l_a = SystemFile("a", 1024, True)
        l_aa = SystemFile("aa", 512, False)
        l_a.add_child(l_aa)
        l_ab = SystemFile("ab", 512, False)
        l_a.add_child(l_ab)
        l_b = SystemFile("b", 1611, True)
        l_ba = SystemFile("ba", 512, True)
        l_b.add_child(l_ba)
        l_baa = SystemFile("baa", 512, False)
        l_ba.add_child(l_baa)
        l_bc = SystemFile("bc", 99, True)  # only in local
        l_b.add_child(l_bc)
        l_bca = SystemFile("bca", 99, False)  # only in local
        l_bc.add_child(l_bca)
        l_bd = SystemFile("bd", 1000, False)
        l_b.add_child(l_bd)

        s_b = LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.RUNNING, "b", "")
        s_b.total_transfer_state = LftpJobStatus.TransferState(1611, 3090, 52, 10, 1000)
        s_b.add_active_file_transfer_state("ba/baa", LftpJobStatus.TransferState(512, 2048, 25, 5, 500))
        s_c = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "c", "")
        s_d = LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.QUEUED, "d", "")

        self.model_builder.set_remote_files([r_a, r_b, r_c, r_d])
        self.model_builder.set_local_files([l_a, l_b])
        self.model_builder.set_lftp_statuses([s_b, s_c, s_d])
        return self.model_builder.build_model()

    def test_build_file_names(self):
        remote_files = [SystemFile("a", 0, False), SystemFile("b", 0, False)]
        local_files = [SystemFile("b", 0, False), SystemFile("c", 0, False)]
        statuses = [LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "b", ""),
                    LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "d", "")]
        self.model_builder.set_remote_files(remote_files)
        self.model_builder.set_local_files(local_files)
        self.model_builder.set_lftp_statuses(statuses)
        model = self.model_builder.build_model()
        self.assertEqual({"a", "b", "c", "d"}, model.get_file_names())

    def test_build_is_dir(self):
        # remote
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 0, False)])
        model = self.model_builder.build_model()
        self.assertEqual(False, model.get_file("a").is_dir)
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 0, True)])
        model = self.model_builder.build_model()
        self.assertEqual(True, model.get_file("a").is_dir)

        # local
        self.model_builder.clear()
        self.model_builder.set_local_files([SystemFile("a", 0, False)])
        model = self.model_builder.build_model()
        self.assertEqual(False, model.get_file("a").is_dir)
        self.model_builder.clear()
        self.model_builder.set_local_files([SystemFile("a", 0, True)])
        model = self.model_builder.build_model()
        self.assertEqual(True, model.get_file("a").is_dir)

        # statuses
        self.model_builder.clear()
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(False, model.get_file("a").is_dir)
        self.model_builder.clear()
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(True, model.get_file("a").is_dir)

        # all three
        self.model_builder.set_remote_files([SystemFile("a", 0, False)])
        self.model_builder.set_local_files([SystemFile("a", 0, False)])
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(False, model.get_file("a").is_dir)
        self.model_builder.set_remote_files([SystemFile("a", 0, True)])
        self.model_builder.set_local_files([SystemFile("a", 0, True)])
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(True, model.get_file("a").is_dir)

    def test_build_mismatch_is_dir(self):
        """Mismatching is_dir raises error"""
        # remote mismatches
        self.model_builder.set_remote_files([SystemFile("a", 0, True)])
        self.model_builder.set_local_files([SystemFile("a", 0, False)])
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        with self.assertRaises(ModelError) as context:
            self.model_builder.build_model()
        self.assertTrue(str(context.exception).startswith("Mismatch in is_dir"))

        # local mismatches
        self.model_builder.set_remote_files([SystemFile("a", 0, False)])
        self.model_builder.set_local_files([SystemFile("a", 0, True)])
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        with self.assertRaises(ModelError) as context:
            self.model_builder.build_model()
        self.assertTrue(str(context.exception).startswith("Mismatch in is_dir"))

        # status mismatches
        self.model_builder.set_remote_files([SystemFile("a", 0, False)])
        self.model_builder.set_local_files([SystemFile("a", 0, False)])
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.QUEUED, "a", "")
        ])
        with self.assertRaises(ModelError) as context:
            self.model_builder.build_model()
        self.assertTrue(str(context.exception).startswith("Mismatch in is_dir"))

    def test_build_state(self):
        # Queued
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 0, False)])
        self.model_builder.set_local_files([SystemFile("a", 0, False)])
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.QUEUED, model.get_file("a").state)

        # Downloading
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 0, False)])
        self.model_builder.set_local_files([SystemFile("a", 0, False)])
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.DOWNLOADING, model.get_file("a").state)

        # Default
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 100, False)])
        self.model_builder.set_local_files([SystemFile("a", 0, False)])
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.DEFAULT, model.get_file("a").state)

        # Default - local only
        self.model_builder.clear()
        self.model_builder.set_local_files([SystemFile("a", 100, False)])
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.DEFAULT, model.get_file("a").state)

        # Downloaded
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 100, False)])
        self.model_builder.set_local_files([SystemFile("a", 100, False)])
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.DOWNLOADED, model.get_file("a").state)

        # Deleted
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 100, False)])
        self.model_builder.set_downloaded_files({"a"})
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.DELETED, model.get_file("a").state)

        # Deleted but Queued
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 100, False)])
        self.model_builder.set_downloaded_files({"a"})
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.QUEUED, model.get_file("a").state)

        # Deleted but Downloading
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 100, False)])
        self.model_builder.set_downloaded_files({"a"})
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.DOWNLOADING, model.get_file("a").state)

        # Deleted, then partially Downloaded
        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 100, False)])
        self.model_builder.set_local_files([SystemFile("a", 50, False)])
        self.model_builder.set_downloaded_files({"a"})
        model = self.model_builder.build_model()
        self.assertEqual(ModelFile.State.DEFAULT, model.get_file("a").state)

    def test_build_remote_size(self):
        self.model_builder.set_remote_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(42, model.get_file("a").remote_size)

        self.model_builder.clear()
        self.model_builder.set_local_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").remote_size)

        self.model_builder.clear()
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").remote_size)

    def test_build_remote_size_from_status_is_ignored(self):
        self.model_builder.set_remote_files([SystemFile("a", 42, False)])
        s = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        s.total_transfer_state = LftpJobStatus.TransferState(None, 12345, None, None, None)
        self.model_builder.set_lftp_statuses([s])
        model = self.model_builder.build_model()
        self.assertEqual(42, model.get_file("a").remote_size)

    def test_build_local_size(self):
        self.model_builder.set_local_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(42, model.get_file("a").local_size)

        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").local_size)

        self.model_builder.clear()
        self.model_builder.set_lftp_statuses([
            LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.QUEUED, "a", "")
        ])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").local_size)

    def test_build_local_size_from_status_is_ignored(self):
        self.model_builder.set_local_files([SystemFile("a", 42, False)])
        s = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        s.total_transfer_state = LftpJobStatus.TransferState(12345, 1000, 0.25, None, None)
        self.model_builder.set_lftp_statuses([s])
        model = self.model_builder.build_model()
        self.assertEqual(42, model.get_file("a").local_size)

    def test_build_local_size_downloading(self):
        self.model_builder.set_local_files([SystemFile("a", 42, False)])
        self.model_builder.set_downloading_files([SystemFile("a", 99, False)])
        s = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        s.total_transfer_state = LftpJobStatus.TransferState(12345, 1000, 0.25, None, None)
        self.model_builder.set_lftp_statuses([s])
        model = self.model_builder.build_model()
        self.assertEqual(99, model.get_file("a").local_size)

    def test_build_downloading_speed(self):
        s = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        s.total_transfer_state = LftpJobStatus.TransferState(None, None, None, 1234, None)
        self.model_builder.set_lftp_statuses([s])
        model = self.model_builder.build_model()
        self.assertEqual(1234, model.get_file("a").downloading_speed)

        self.model_builder.clear()
        s = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        self.model_builder.set_lftp_statuses([s])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").downloading_speed)

        self.model_builder.clear()
        self.model_builder.set_local_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").downloading_speed)

        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").downloading_speed)

    def test_build_eta(self):
        s = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        s.total_transfer_state = LftpJobStatus.TransferState(None, None, None, None, 4567)
        self.model_builder.set_lftp_statuses([s])
        model = self.model_builder.build_model()
        self.assertEqual(4567, model.get_file("a").eta)

        self.model_builder.clear()
        s = LftpJobStatus(0, LftpJobStatus.Type.PGET, LftpJobStatus.State.RUNNING, "a", "")
        self.model_builder.set_lftp_statuses([s])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").eta)

        self.model_builder.clear()
        self.model_builder.set_local_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").eta)

        self.model_builder.clear()
        self.model_builder.set_remote_files([SystemFile("a", 42, False)])
        model = self.model_builder.build_model()
        self.assertEqual(None, model.get_file("a").eta)

    def test_build_children_names(self):
        model = self.__build_test_model_children_tree_1()
        self.assertEqual({"a", "b", "c", "d"}, model.get_file_names())
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        self.assertEqual({"aa", "ab"}, m_a_ch.keys())
        m_b_ch = {m.name: m for m in model.get_file("b").get_children()}
        self.assertEqual({"ba", "bb", "bc", "bd"}, m_b_ch.keys())
        m_ba_ch = {m.name: m for m in m_b_ch["ba"].get_children()}
        self.assertEqual({"baa"}, m_ba_ch.keys())
        m_baa_ch = {m.name: m for m in m_ba_ch["baa"].get_children()}
        self.assertEqual(0, len(m_baa_ch.keys()))
        m_bb_ch = {m.name: m for m in m_b_ch["bb"].get_children()}
        self.assertEqual({"bba"}, m_bb_ch.keys())
        m_bba_ch = {m.name: m for m in m_bb_ch["bba"].get_children()}
        self.assertEqual(0, len(m_bba_ch.keys()))
        m_bc_ch = {m.name: m for m in m_b_ch["bc"].get_children()}
        self.assertEqual({"bca"}, m_bc_ch.keys())
        m_bca_ch = {m.name: m for m in m_bc_ch["bca"].get_children()}
        self.assertEqual(0, len(m_bca_ch.keys()))
        m_c_ch = {m.name: m for m in model.get_file("c").get_children()}
        self.assertEqual(0, len(m_c_ch.keys()))
        m_d_ch = {m.name: m for m in model.get_file("d").get_children()}
        self.assertEqual({"da"}, m_d_ch.keys())
        m_da_ch = {m.name: m for m in m_d_ch["da"].get_children()}
        self.assertEqual(0, len(m_da_ch.keys()))

    def test_build_children_is_dir(self):
        model = self.__build_test_model_children_tree_1()
        m_a = model.get_file("a")
        self.assertEqual(True, m_a.is_dir)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(False, m_aa.is_dir)
        m_ab = m_a_ch["ab"]
        self.assertEqual(False, m_ab.is_dir)
        m_b = model.get_file("b")
        self.assertEqual(True, m_b.is_dir)
        m_b_ch = {m.name: m for m in model.get_file("b").get_children()}
        m_ba = m_b_ch["ba"]
        self.assertEqual(True, m_ba.is_dir)
        m_baa = m_ba.get_children()[0]
        self.assertEqual(False, m_baa.is_dir)
        m_bb = m_b_ch["bb"]
        self.assertEqual(True, m_bb.is_dir)
        m_bba = m_bb.get_children()[0]
        self.assertEqual(False, m_bba.is_dir)
        m_bc = m_b_ch["bc"]
        self.assertEqual(True, m_bc.is_dir)
        m_bca = m_bc.get_children()[0]
        self.assertEqual(False, m_bca.is_dir)
        m_bd = m_b_ch["bd"]
        self.assertEqual(False, m_bd.is_dir)
        m_c = model.get_file("c")
        self.assertEqual(False, m_c.is_dir)
        m_d = model.get_file("d")
        self.assertEqual(True, m_d.is_dir)
        m_d_ch = {m.name: m for m in model.get_file("d").get_children()}
        m_da = m_d_ch["da"]
        self.assertEqual(False, m_da.is_dir)

    def test_build_children_mismatch_is_dir(self):
        """Mismatching is_dir in a child raises error"""
        r_a = SystemFile("a", 0, True)
        r_aa = SystemFile("aa", 0, True)
        r_a.add_child(r_aa)
        l_a = SystemFile("a", 0, True)
        l_aa = SystemFile("aa", 0, False)
        l_a.add_child(l_aa)
        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([l_a])
        with self.assertRaises(ModelError) as context:
            self.model_builder.build_model()
        self.assertTrue(str(context.exception).startswith("Mismatch in is_dir between child"))

    def test_build_children_sizes(self):
        model = self.__build_test_model_children_tree_1()
        m_a = model.get_file("a")
        self.assertEqual((1024, 1024), (m_a.remote_size, m_a.local_size))
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual((512, 512), (m_aa.remote_size, m_aa.local_size))
        m_ab = m_a_ch["ab"]
        self.assertEqual((512, 512), (m_ab.remote_size, m_ab.local_size))
        m_b = model.get_file("b")
        self.assertEqual((3090, 1611), (m_b.remote_size, m_b.local_size))
        m_b_ch = {m.name: m for m in model.get_file("b").get_children()}
        m_ba = m_b_ch["ba"]
        self.assertEqual((2048, 512), (m_ba.remote_size, m_ba.local_size))
        m_baa = m_ba.get_children()[0]
        self.assertEqual((2048, 512), (m_baa.remote_size, m_baa.local_size))
        m_bb = m_b_ch["bb"]
        self.assertEqual((42, None), (m_bb.remote_size, m_bb.local_size))
        m_bba = m_bb.get_children()[0]
        self.assertEqual((42, None), (m_bba.remote_size, m_bba.local_size))
        m_bc = m_b_ch["bc"]
        self.assertEqual((None, 99), (m_bc.remote_size, m_bc.local_size))
        m_bca = m_bc.get_children()[0]
        self.assertEqual((None, 99), (m_bca.remote_size, m_bca.local_size))
        m_bd = m_b_ch["bd"]
        self.assertEqual((1000, 1000), (m_bd.remote_size, m_bd.local_size))
        m_c = model.get_file("c")
        self.assertEqual((1234, None), (m_c.remote_size, m_c.local_size))
        m_d = model.get_file("d")
        self.assertEqual((5678, None), (m_d.remote_size, m_d.local_size))
        m_d_ch = {m.name: m for m in model.get_file("d").get_children()}
        m_da = m_d_ch["da"]
        self.assertEqual((5678, None), (m_da.remote_size, m_da.local_size))

    def test_build_children_state_default(self):
        """File only exists remotely"""
        r_a = SystemFile("a", 300, True)
        r_aa = SystemFile("aa", 100, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 100, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 200, False)
        r_a.add_child(r_ab)

        self.model_builder.set_remote_files([r_a])
        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DEFAULT, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DEFAULT, m_ab.state)

    def test_build_children_state_default_partial(self):
        """File is partially downloaded"""
        r_a = SystemFile("a", 300, True)
        r_aa = SystemFile("aa", 100, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 100, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 200, False)
        r_a.add_child(r_ab)

        l_a = SystemFile("a", 150, True)
        l_aa = SystemFile("aa", 50, True)
        l_a.add_child(l_aa)
        l_aaa = SystemFile("aaa", 50, False)
        l_aa.add_child(l_aaa)
        l_ab = SystemFile("ab", 100, False)
        l_a.add_child(l_ab)

        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([l_a])
        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DEFAULT, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DEFAULT, m_ab.state)

    def test_build_children_state_default_extra(self):
        """File only exists locally"""
        l_a = SystemFile("a", 150, True)
        l_aa = SystemFile("aa", 50, True)
        l_a.add_child(l_aa)
        l_aaa = SystemFile("aaa", 50, False)
        l_aa.add_child(l_aaa)
        l_ab = SystemFile("ab", 100, False)
        l_a.add_child(l_ab)

        self.model_builder.set_local_files([l_a])
        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DEFAULT, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DEFAULT, m_ab.state)

    def test_build_children_state_downloaded_full(self):
        r_a = SystemFile("a", 300, True)
        r_aa = SystemFile("aa", 100, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 100, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 200, False)
        r_a.add_child(r_ab)

        l_a = SystemFile("a", 300, True)
        l_aa = SystemFile("aa", 100, True)
        l_a.add_child(l_aa)
        l_aaa = SystemFile("aaa", 100, False)
        l_aa.add_child(l_aaa)
        l_ab = SystemFile("ab", 200, False)
        l_a.add_child(l_ab)

        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([l_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DOWNLOADED, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_ab.state)

    def test_build_children_state_downloaded_full_extra(self):
        """Fully downloaded but with an extra local-only file"""
        r_a = SystemFile("a", 300, True)
        r_aa = SystemFile("aa", 100, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 100, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 200, False)
        r_a.add_child(r_ab)

        l_a = SystemFile("a", 400, True)
        l_aa = SystemFile("aa", 100, True)
        l_a.add_child(l_aa)
        l_aaa = SystemFile("aaa", 100, False)
        l_aa.add_child(l_aaa)
        l_ab = SystemFile("ab", 200, False)
        l_a.add_child(l_ab)
        l_ac = SystemFile("ac", 100, True)  # local only
        l_a.add_child(l_ac)
        l_aca = SystemFile("aca", 100, False)  # local only
        l_ac.add_child(l_aca)

        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([l_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DOWNLOADED, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_ab.state)
        l_ac = SystemFile("ac", 100, True)  # local only
        l_a.add_child(l_ac)
        l_aca = SystemFile("aca", 100, False)  # local only
        l_ac.add_child(l_aca)

    def test_build_children_state_downloaded_partial(self):
        r_a = SystemFile("a", 300, True)
        r_aa = SystemFile("aa", 100, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 100, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 200, False)
        r_a.add_child(r_ab)

        l_a = SystemFile("a", 250, True)
        l_aa = SystemFile("aa", 50, True)
        l_a.add_child(l_aa)
        l_aaa = SystemFile("aaa", 50, False)
        l_aa.add_child(l_aaa)
        l_ab = SystemFile("ab", 200, False)
        l_a.add_child(l_ab)

        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([l_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DEFAULT, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_ab.state)

    def test_build_children_state_downloaded_partial_extra(self):
        """Partially downloaded but with an extra local-only file"""
        r_a = SystemFile("a", 300, True)
        r_aa = SystemFile("aa", 100, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 100, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 200, False)
        r_a.add_child(r_ab)

        l_a = SystemFile("a", 350, True)
        l_aa = SystemFile("aa", 50, True)
        l_a.add_child(l_aa)
        l_aaa = SystemFile("aaa", 50, False)
        l_aa.add_child(l_aaa)
        l_ab = SystemFile("ab", 200, False)
        l_a.add_child(l_ab)
        l_ac = SystemFile("ac", 100, True)  # local only
        l_a.add_child(l_ac)
        l_aca = SystemFile("aca", 100, False)  # local only
        l_ac.add_child(l_aca)

        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([l_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DEFAULT, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_ab.state)
        m_ac = m_a_ch["ac"]
        self.assertEqual(ModelFile.State.DEFAULT, m_ac.state)
        m_aca = m_ac.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_aca.state)

    def test_build_children_state_queued(self):
        r_a = SystemFile("a", 0, True)
        r_aa = SystemFile("aa", 0, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 0, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 0, False)
        r_a.add_child(r_ab)
        s_a = LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.QUEUED, "a", "")
        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_lftp_statuses([s_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.QUEUED, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.QUEUED, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.QUEUED, m_ab.state)

    def test_build_children_state_downloading_1(self):
        # Child files are active
        r_a = SystemFile("a", 0, True)
        r_aa = SystemFile("aa", 0, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 0, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 0, False)
        r_a.add_child(r_ab)
        s_a = LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.RUNNING, "a", "")
        s_a.add_active_file_transfer_state("aa/aaa", LftpJobStatus.TransferState(None, None, None, None, None))
        s_a.add_active_file_transfer_state("ab", LftpJobStatus.TransferState(None, None, None, None, None))
        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_lftp_statuses([s_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DOWNLOADING, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DOWNLOADING, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DOWNLOADING, m_ab.state)

    def test_build_children_state_downloading_2(self):
        # Child files are finished
        r_a = SystemFile("a", 150, True)
        r_aa = SystemFile("aa", 100, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 100, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 50, False)
        r_a.add_child(r_ab)

        s_a = LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.RUNNING, "a", "")
        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([r_a])
        self.model_builder.set_lftp_statuses([s_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DOWNLOADING, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_ab.state)

    def test_build_children_state_downloading_3(self):
        # Child files are queued
        r_a = SystemFile("a", 0, True)
        r_aa = SystemFile("aa", 0, True)
        r_a.add_child(r_aa)
        r_aaa = SystemFile("aaa", 0, False)
        r_aa.add_child(r_aaa)
        r_ab = SystemFile("ab", 0, False)
        r_a.add_child(r_ab)
        s_a = LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.RUNNING, "a", "")
        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_lftp_statuses([s_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DOWNLOADING, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.QUEUED, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.QUEUED, m_ab.state)

    def test_build_children_state_downloading_4(self):
        # Child files are only present in local
        r_a = SystemFile("a", 0, True)
        r_aa = SystemFile("aa", 0, True)
        r_a.add_child(r_aa)
        l_a = SystemFile("a", 0, True)
        l_aa = SystemFile("aa", 0, True)
        l_a.add_child(l_aa)
        l_aaa = SystemFile("aaa", 0, False)
        l_aa.add_child(l_aaa)
        l_ab = SystemFile("ab", 0, False)
        l_a.add_child(l_ab)
        s_a = LftpJobStatus(0, LftpJobStatus.Type.MIRROR, LftpJobStatus.State.RUNNING, "a", "")
        self.model_builder.set_remote_files([r_a])
        self.model_builder.set_local_files([l_a])
        self.model_builder.set_lftp_statuses([s_a])

        model = self.model_builder.build_model()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DOWNLOADING, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DEFAULT, m_aa.state)
        m_aaa = m_aa.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_aaa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DEFAULT, m_ab.state)

    def test_build_children_state_all(self):
        model = self.__build_test_model_children_tree_1()
        m_a = model.get_file("a")
        self.assertEqual(ModelFile.State.DOWNLOADED, m_a.state)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_aa.state)
        m_ab = m_a_ch["ab"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_ab.state)
        m_b = model.get_file("b")
        self.assertEqual(ModelFile.State.DOWNLOADING, m_b.state)
        m_b_ch = {m.name: m for m in model.get_file("b").get_children()}
        m_ba = m_b_ch["ba"]
        self.assertEqual(ModelFile.State.DEFAULT, m_ba.state)
        m_baa = m_ba.get_children()[0]
        self.assertEqual(ModelFile.State.DOWNLOADING, m_baa.state)
        m_bb = m_b_ch["bb"]
        self.assertEqual(ModelFile.State.DEFAULT, m_bb.state)
        m_bba = m_bb.get_children()[0]
        self.assertEqual(ModelFile.State.QUEUED, m_bba.state)
        m_bc = m_b_ch["bc"]
        self.assertEqual(ModelFile.State.DEFAULT, m_bc.state)
        m_bca = m_bc.get_children()[0]
        self.assertEqual(ModelFile.State.DEFAULT, m_bca.state)
        m_bd = m_b_ch["bd"]
        self.assertEqual(ModelFile.State.DOWNLOADED, m_bd.state)
        m_c = model.get_file("c")
        self.assertEqual(ModelFile.State.QUEUED, m_c.state)
        m_d = model.get_file("d")
        self.assertEqual(ModelFile.State.QUEUED, m_d.state)
        m_d_ch = {m.name: m for m in model.get_file("d").get_children()}
        m_da = m_d_ch["da"]
        self.assertEqual(ModelFile.State.QUEUED, m_da.state)

    def test_build_children_downloading_speed(self):
        model = self.__build_test_model_children_tree_1()
        m_a = model.get_file("a")
        self.assertEqual(None, m_a.downloading_speed)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(None, m_aa.downloading_speed)
        m_ab = m_a_ch["ab"]
        self.assertEqual(None, m_ab.downloading_speed)
        m_b = model.get_file("b")
        self.assertEqual(10, m_b.downloading_speed)
        m_b_ch = {m.name: m for m in model.get_file("b").get_children()}
        m_ba = m_b_ch["ba"]
        self.assertEqual(None, m_ba.downloading_speed)
        m_baa = m_ba.get_children()[0]
        self.assertEqual(5, m_baa.downloading_speed)
        m_bb = m_b_ch["bb"]
        self.assertEqual(None, m_bb.downloading_speed)
        m_bba = m_bb.get_children()[0]
        self.assertEqual(None, m_bba.downloading_speed)
        m_bc = m_b_ch["bc"]
        self.assertEqual(None, m_bc.downloading_speed)
        m_bca = m_bc.get_children()[0]
        self.assertEqual(None, m_bca.downloading_speed)
        m_bd = m_b_ch["bd"]
        self.assertEqual(None, m_bd.downloading_speed)
        m_c = model.get_file("c")
        self.assertEqual(None, m_c.downloading_speed)
        m_d = model.get_file("d")
        self.assertEqual(None, m_d.downloading_speed)
        m_d_ch = {m.name: m for m in model.get_file("d").get_children()}
        m_da = m_d_ch["da"]
        self.assertEqual(None, m_da.downloading_speed)

    def test_build_children_eta(self):
        model = self.__build_test_model_children_tree_1()
        m_a = model.get_file("a")
        self.assertEqual(None, m_a.eta)
        m_a_ch = {m.name: m for m in model.get_file("a").get_children()}
        m_aa = m_a_ch["aa"]
        self.assertEqual(None, m_aa.eta)
        m_ab = m_a_ch["ab"]
        self.assertEqual(None, m_ab.eta)
        m_b = model.get_file("b")
        self.assertEqual(1000, m_b.eta)
        m_b_ch = {m.name: m for m in model.get_file("b").get_children()}
        m_ba = m_b_ch["ba"]
        self.assertEqual(None, m_ba.eta)
        m_baa = m_ba.get_children()[0]
        self.assertEqual(500, m_baa.eta)
        m_bb = m_b_ch["bb"]
        self.assertEqual(None, m_bb.eta)
        m_bba = m_bb.get_children()[0]
        self.assertEqual(None, m_bba.eta)
        m_bc = m_b_ch["bc"]
        self.assertEqual(None, m_bc.eta)
        m_bca = m_bc.get_children()[0]
        self.assertEqual(None, m_bca.eta)
        m_bd = m_b_ch["bd"]
        self.assertEqual(None, m_bd.eta)
        m_c = model.get_file("c")
        self.assertEqual(None, m_c.eta)
        m_d = model.get_file("d")
        self.assertEqual(None, m_d.eta)
        m_d_ch = {m.name: m for m in model.get_file("d").get_children()}
        m_da = m_d_ch["da"]
        self.assertEqual(None, m_da.eta)
