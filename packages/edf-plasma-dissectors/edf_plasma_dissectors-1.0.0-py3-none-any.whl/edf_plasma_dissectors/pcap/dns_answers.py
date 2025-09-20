"""PCAP DNS Answers artifact dissector"""

from edf_plasma_core.concept import Tag
from edf_plasma_core.dissector import (
    DissectionContext,
    Dissector,
    register_dissector,
)
from edf_plasma_core.helper.table import Column, DataType
from edf_plasma_core.helper.typing import RecordIterator
from scapy.layers.dns import DNS, dnstypes

from .helper import (
    decode_utf8_string,
    pkt_base_record,
    select_pcap_impl,
    stream_pcap_packets,
)


def _dissect_https(answer) -> RecordIterator:
    for svc_param in answer.svc_params:
        if svc_param.key not in {4, 6}:  # ipv4hint or ipv6hint
            continue
        for value in svc_param.value:
            yield {
                'dns_r_name': decode_utf8_string(answer.rrname),
                'dns_r_type': dnstypes[answer.type],
                'dns_r_data': value,
            }


def _dissect_default(answer) -> RecordIterator:
    yield {
        'dns_r_name': decode_utf8_string(answer.rrname),
        'dns_r_type': dnstypes[answer.type],
        'dns_r_data': decode_utf8_string(answer.rdata),
    }


_DISSECT_STRATEGY = {
    'HTTPS': _dissect_https,
}


def _dissect_impl(ctx: DissectionContext) -> RecordIterator:
    for pkt in stream_pcap_packets(ctx.filepath):
        if DNS not in pkt:
            continue
        if not pkt[DNS].qr or not pkt[DNS].ancount:
            continue
        record = pkt_base_record(pkt)
        if not record:
            continue
        answers = pkt[DNS].an
        for answer in answers:
            dns_r_type = dnstypes[answer.type]
            _dissect = _DISSECT_STRATEGY.get(dns_r_type, _dissect_default)
            for extra in _dissect(answer):
                record.update(extra)
                yield record


DISSECTOR = Dissector(
    slug='pcap_dns_answers',
    tags={Tag.PCAP},
    columns=[
        Column('pkt_time', DataType.STR),
        Column('pkt_src_ip', DataType.INET),
        Column('pkt_src_port', DataType.INT),
        Column('pkt_dst_ip', DataType.INET),
        Column('pkt_dst_port', DataType.INT),
        Column('dns_r_name', DataType.STR),
        Column('dns_r_type', DataType.STR),
        Column('dns_r_data', DataType.STR),
    ],
    description="DNS answers from PCAP",
    select_impl=select_pcap_impl,
    dissect_impl=_dissect_impl,
)
register_dissector(DISSECTOR)
