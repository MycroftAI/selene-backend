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

from .preferences import PreferencesEndpoint
from .city import CityEndpoint
from .country import CountryEndpoint
from .defaults import AccountDefaultsEndpoint
from .device import DeviceEndpoint
from .device_count import DeviceCountEndpoint
from .geography import GeographyEndpoint
from .membership import MembershipEndpoint
from .pairing_code import PairingCodeEndpoint
from .region import RegionEndpoint
from .skills import SkillsEndpoint
from .skill_oauth import SkillOauthEndpoint
from .skill_settings import SkillSettingsEndpoint
from .timezone import TimezoneEndpoint
from .voice_endpoint import VoiceEndpoint
from .wake_word_endpoint import WakeWordEndpoint
