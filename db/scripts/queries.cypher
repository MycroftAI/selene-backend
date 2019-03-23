users.csv
match (n:User) return n.uuid, n.email, n.password, n.termsOfUseDate, n.privacyPolicyDate

subscription.csv
match (n) where ((n:MonthlyAccount) or (n:YearlyAccount)) and n.expiratesAt is not null set n.expiresAt = n.expiratesAt

match (n:User)-[:ACCOUNT]->(acc)
where not (acc:FreeAccount)
return n.uuid, acc.customerId, acc.lastPayment, labels(acc)[0]

user_location.csv
match (n:User)-[:LIVES_AT]->()-[:COORDINATE]->(coord) return n.uuid, coord.latitude, coord.longitude

user_setting.csv
match (n:User)-[:SETTING]->(setting)-[:TTS_SETTING]->(tts:Active), (setting)-[:LISTENER_SETTING]->(listener)
with filter(l in labels(tts) where l <> 'Active') as s, n, tts, setting, listener
return n.uuid, setting.dateFormat, setting.timeFormat, setting.systemUnit, s[0], tts.voice, listener.wakeWord, listener.sampleRate, listener.channels, listener.phonemes, listener.threshold, listener.multiplier, listener.energyRatio

device.csv
match (user:User)-[:DEVICE]->(n:Device) return n.uuid, user.uuid, n.name, n.description, n.platform, n.enclosureVersion, n.coreVersion

devices_location.csv
match (n:Device)-[:PLACED_AT]->()-[:COORDINATE]->(coord) return n.uuid, coord.latitude, coord.longitude

skill.csv
match (dev:Device)-[:SKILL_MAPPING]->()-[:SKILL]->(n:Skill) return n.uuid, dev.uuid, n.name, n.description, n.identifier, n.color

skill_section.csv
match (skill:Skill)-[:METADATA]->()-[:SECTION]->(section) return section.uuid, skill.uuid, section.name, section.order order by skill.uuid

skill_fields.csv
match (section:SkillMetadataSection)-[:FIELD]->(field:SkillMetadataField) return field.uuid, section.uuid, field.name, field.type, field.label, field.hint, field.placeholder, field.hide, field.options, field.order

skill_fields_values.csv
match (device:Device)-[:SKILL_MAPPING]->(map:SkillMetadataMapping)-[r:SKILL_FIELD_VALUE]->(field:SkillMetadataField), (map)-[:SKILL]->(skill:Skill) return field.uuid, skill.uuid, device.uuid, r.value

location.csv
match (l:Location)-[:TIMEZONE]->(t:Timezone), (l)-[:IN]->(c:City) return l.uuid, t.uuid, c.uuid

timezone.csv
match (n:Timezone) return n.uuid, n.name

city.csv
match (country)-[:STATE]->(state:State)-[:CITY]->(city:City) return city.uuid, state.uuid, city.name

region.csv
match (country)-[:STATE]->(state:State)-[:CITY]->(city:City) return state.uuid, country.uuid, state.name

country.csv
match (country)-[:STATE]->(state:State)-[:CITY]->(city:City) return country.uuid, state.code, state.name

device_location.csv
match (d:Device)-[:PLACED_AT]->(l:Location) return d.uuid, l.uuid