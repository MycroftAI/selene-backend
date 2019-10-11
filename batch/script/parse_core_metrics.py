# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Convert the raw timing metrics from core into a format for latency profiling.

The raw core metric data is stored in a JSON object in the metric.core table.
There is a row on the metric.core table for each step in each user interaction.
This format is not ideal for querying timing statistics for latency profiling.

Combine the pertinent data from all steps in an interaction into a single row
on the metric.core_interaction table.
"""
from datetime import datetime
from decimal import Decimal

from selene.batch import SeleneScript
from selene.data.metric import CoreMetricRepository, CoreInteraction

SKILL_HANDLERS_TO_SKIP = ('reset', 'notify', 'prime', 'stop_laugh')


class CoreMetricsParser(SeleneScript):
    def __init__(self):
        super(CoreMetricsParser, self).__init__(__file__)
        self.core_metric_repo = CoreMetricRepository(self.db)
        self.interaction_cnt = 0
        self.interaction: CoreInteraction = None
        self.stt_start_ts = None
        self.playback_start_ts = None

    def _run(self):
        last_interaction_id = None
        for metric in self.core_metric_repo.get_metrics_by_date(self.args.date):
            if metric.metric_value['id'] != last_interaction_id:
                self._add_interaction_to_db()
                self._start_new_interaction(metric)
                last_interaction_id = self.interaction.core_id
            self._add_metric_to_interaction(metric.metric_value)
        self._add_interaction_to_db()

    def _start_new_interaction(self, metric):
        """Initialize the interaction object"""
        self.interaction = CoreInteraction(
            core_id=metric.metric_value['id'],
            device_id=metric.device_id,
            start_ts=datetime.utcfromtimestamp(
                metric.metric_value['start_time']
            ),
        )
        self.stt_start_ts = None
        self.playback_start_ts = None

    def _add_metric_to_interaction(self, metric_value):
        """Combine all the steps of an interaction into a single record"""
        duration = Decimal(str(metric_value['time']))
        duration = duration.quantize(Decimal('0.000001'))
        if metric_value['system'] == 'stt':
            self.interaction.stt_engine = metric_value['stt']
            self.interaction.stt_transcription = metric_value['transcription']
            self.interaction.stt_duration = duration
            self.stt_start_ts = metric_value['start_time']
        elif metric_value['system'] == 'intent_service':
            self.interaction.intent_type = metric_value['intent_type']
            self.interaction.intent_duration = duration
        elif metric_value['system'] == 'fallback_handler':
            self.interaction.fallback_handler_duration = duration
        elif metric_value['system'] == 'skill_handler':
            if metric_value['handler'] not in SKILL_HANDLERS_TO_SKIP:
                self.interaction.skill_handler = metric_value['handler']
                self.interaction.skill_duration = duration
        elif metric_value['system'] == 'speech':
            self.interaction.tts_engine = metric_value['tts']
            self.interaction.tts_utterance = metric_value['utterance']
            self.interaction.tts_duration = duration
        elif metric_value['system'] == 'speech_playback':
            self.interaction.speech_playback_duration = duration
            self.playback_start_ts = metric_value['start_time']

        # The user-experienced latency is the time between when the user
        # finishes speaking their intent and when the device provides a voice
        # response.
        if self.stt_start_ts is not None and self.playback_start_ts is not None:
            self.interaction.user_latency = (
                    self.playback_start_ts - self.stt_start_ts
            )

    def _add_interaction_to_db(self):
        if self.interaction is not None:
            if self.interaction.stt_transcription is not None:
                self.interaction_cnt += 1
                self.core_metric_repo.add_interaction(self.interaction)


if __name__ == '__main__':
    CoreMetricsParser().run()
