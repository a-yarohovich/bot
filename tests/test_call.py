import asyncio
import unittest
import uuid
from unittest.mock import Mock

import async_db_adapter as db
from core import call
from core import global_event_loop as gloop
from core import utilites as util


class CallUnitTests(unittest.TestCase):
    def setUp(self):
        self.icall = call.CallImpl(
            uuid.uuid4(),
            uuid.uuid4(),
            "calling-ajrfhweui64r2378642uhdbnv/j.,",
            "called-asdjfhweuiry"
        )

    def tearDown(self):
        pass

    def test_str_represent(self):
        print(self.icall)
        self.assertTrue(str(self.icall))

    def test_repr_represent(self):
        print(repr(self.icall))
        self.assertTrue(repr(self.icall))

    def test_call_event_answer_1(self):
        msg = """
        {"Event-Name":"CHANNEL_ANSWER","Core-UUID":"7d27b126-92d7-497e-b5e8-3e7bf20a7cea",
        "FreeSWITCH-Hostname":"ip-172-31-34-102","FreeSWITCH-Switchname":"ip-172-31-34-102",
        "FreeSWITCH-IPv4":"172.31.34.102","FreeSWITCH-IPv6":"::1","Event-Date-Local":"2017-11-18 09:09:58",
        "Event-Date-GMT":"Sat, 18 Nov 2017 09:09:58 GMT","Event-Date-Timestamp":"1510996198267012",
        "Event-Calling-File":"switch_channel.c","Event-Calling-Function":"switch_channel_perform_mark_answered",
        "variable_app_context_uuid":"8cd16178-5681-4c48-b04c-91d9ba55fc34",
        "variable_origination_caller_id_number":"9999","variable_originate_early_media":"true"}
        """
        self.icall.call_answer(util.parse_json_from_raw_ev(msg))
        self.icall.call_answer(util.parse_json_from_raw_ev(msg))
        self.icall.call_answer(util.parse_json_from_raw_ev(None))
        self.icall.call_answer(None)
        self.assertTrue(self.icall.faanswer_time)
        self.assertEqual(self.icall.call_state, call.CallState.ANSWERED)

        f = Mock()
        def call_answer(icall):
            self.assertTrue(icall)

        f.on_call_answer = call_answer
        self.assertTrue(self.icall.subscribe(f))
        self.icall.call_answer(util.parse_json_from_raw_ev(msg))

    def test_on_call_create_1(self):
        msg = """
        {"Event-Name":"CHANNEL_CREATE","Core-UUID":"7d27b126-92d7-497e-b5e8-3e7bf20a7cea",
        "FreeSWITCH-Hostname":"ip-172-31-34-102","FreeSWITCH-Switchname":"ip-172-31-34-102",
        "FreeSWITCH-IPv4":"172.31.34.102","FreeSWITCH-IPv6":"::1","Event-Date-Local":"2017-11-18 09:09:58",
        "Event-Date-GMT":"Sat, 18 Nov 2017 09:09:58 GMT","Event-Date-Timestamp":"1510996198267012",
        "Event-Calling-File":"switch_channel.c","Event-Calling-Function":"switch_channel_perform_mark_answered",
        "variable_app_context_uuid":"8cd16178-5681-4c48-b04c-91d9ba55fc34",
        "variable_origination_caller_id_number":"9999","variable_originate_early_media":"true"}
        """
        self.icall.call_create(util.parse_json_from_raw_ev(msg))
        self.icall.call_create(util.parse_json_from_raw_ev(msg))
        self.icall.call_create(util.parse_json_from_raw_ev(None))
        self.icall.call_create(None)
        self.assertTrue(self.icall.facreate_time)
        self.assertEqual(self.icall.call_state, call.CallState.CREATED)

    def test_call_event_destroy_1(self):
        msg = """
        {"Event-Name":"CHANNEL_DESTROY","Core-UUID":"7d27b126-92d7-497e-b5e8-3e7bf20a7cea",
        "FreeSWITCH-Hostname":"ip-172-31-34-102","FreeSWITCH-Switchname":"ip-172-31-34-102",
        "FreeSWITCH-IPv4":"172.31.34.102","FreeSWITCH-IPv6":"::1","Event-Date-Local":"2017-11-18 09:09:58",
        "Event-Date-GMT":"Sat, 18 Nov 2017 09:09:58 GMT","Event-Date-Timestamp":"1510996198267012",
        "Event-Calling-File":"switch_channel.c","Event-Calling-Function":"switch_channel_perform_mark_answered",
        "variable_app_context_uuid":"8cd16178-5681-4c48-b04c-91d9ba55fc34",
        "variable_origination_caller_id_number":"9999","variable_originate_early_media":"true"}
        """
        self.icall.call_destroy(util.parse_json_from_raw_ev(msg))
        self.icall.call_destroy(util.parse_json_from_raw_ev(msg))
        self.icall.call_destroy(util.parse_json_from_raw_ev(None))
        self.icall.call_destroy(None)
        self.assertTrue(self.icall.fadestroy_time)
        self.assertEqual(self.icall.call_state, call.CallState.DESTROY)

        f = Mock()
        def call_event_destroy(icall):
            self.assertTrue(icall)

        f.on_call_destroy = call_event_destroy
        self.assertTrue(self.icall.subscribe(f))
        self.icall.call_destroy(util.parse_json_from_raw_ev(msg))

    def test_subscribe(self):
        f = Mock()
        self.assertTrue(self.icall.subscribe(f))
        self.assertFalse(self.icall.subscribe(f))
        self.assertFalse(self.icall.subscribe(f))
        self.assertTrue(self.icall.subscriber_list.count(f))

    def test_unsubscribe(self):
        f = Mock()
        f1= Mock()
        self.assertTrue(self.icall.subscribe(f))
        self.assertFalse(self.icall.subscribe(f))
        self.assertFalse(self.icall.subscribe(f))
        self.assertTrue(self.icall.subscriber_list.count(f))

        self.assertTrue(self.icall.unsubscribe(f))
        self.assertFalse(self.icall.unsubscribe(f))
        self.assertFalse(self.icall.unsubscribe(f1))

    def test_get_id(self):
        self.assertTrue(self.icall.get_id())

    def test_get_calling_number(self):
        self.assertTrue(self.icall.get_calling_number())

    def test_get_called_number(self):
        self.assertTrue(self.icall.get_called_number())

    def test_get_context_id(self):
        self.assertTrue(self.icall.get_context_id())

    def test_get_state(self):
        self.assertTrue(self.icall.get_state())

    def test_flush_cdr(self):
        self.icall.fadestroy_time = db.now()
        self.icall.facreate_time = db.now()
        task = self.icall.flush_cdr()
        self.assertTrue(task)
        asyncio.gather(task)
        # gloop.global_ev_loop.gather(task)



def init_conn_ok(future):
    unittest.main()


if __name__ == '__main__':
    gloop.global_ev_loop.run_until_complete(gloop.push_async_task(init_conn_ok, db.async_create_pg_conn))

