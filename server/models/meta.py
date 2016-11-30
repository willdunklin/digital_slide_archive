import re

from girder.constants import AccessType
from girder.models.model_base import ValidationException

from ..constants import TCGACollectionSettingKey


class TCGAModel(object):
    case_re = re.compile('tcga-[a-z0-9]{2}-[a-z0-9]{4}', flags=re.I)
    uuid_re = re.compile(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        flags=re.I
    )
    barcode_re = re.compile(
        case_re.pattern + '[0-9a-z-]*',
        flags=re.I
    )
    image_re = re.compile(
        '^(?P<barcode>(?P<case>' +
        case_re.pattern + ')[0-9a-z-]*)\.' +
        '(?P<uuid>' + uuid_re.pattern + ')\.svs$',
        flags=re.I
    )
    pathology_re = re.compile(
        '^(?P<case>' + case_re.pattern +
        ')\.(?P<uuid>' + uuid_re.pattern +
        ')\.pdf$',
        flags=re.I
    )

    def initialize(self, **kwargs):
        self.exposeFields(AccessType.READ, fields='tcga')
        super(TCGAModel, self).initialize(**kwargs)

    def save(self, doc, baseModel=False, **kwargs):
        if not baseModel:
            self.setTCGA(doc, type=self.TCGAType)
        return super(TCGAModel, self).save(doc, **kwargs)

    def find(self, query=None, **kwargs):
        query = query or {}
        query['tcga.type'] = self.TCGAType
        return super(TCGAModel, self).find(query, **kwargs)

    def findOne(self, query=None, **kwargs):
        query = query or {}
        query['tcga.type'] = self.TCGAType
        return super(TCGAModel, self).findOne(query, **kwargs)

    def setTCGA(self, doc, **tcga):
        self.getTCGA(doc).update(tcga)

    def getTCGA(self, doc):
        if 'tcga' not in doc:
            doc['tcga'] = {}
        return doc['tcga']

    def removeTCGA(self, doc):
        del doc['tcga']
        self.save(doc, baseModel=True)
        return doc

    def getTCGAType(self, doc):
        return self.getTCGA(doc).get('type')

    def getTCGACollection(self):
        tcga = self.model('setting').get(
            TCGACollectionSettingKey
        )
        if tcga is None:
            raise Exception(
                'TCGA collection id not initialized in settings'
            )
        return self.model('collection').load(
            tcga, force=True
        )

    def _parse(self, name, regex):
        m = regex.match(name)
        if m is None:
            raise ValidationException('Invalid name')
        return m.groupdict()

    def parseImage(self, name):
        return self._parse(name, self.image_re)

    def parsePathology(self, name):
        return self._parse(name, self.pathology_re)

    def importDocument(self, doc, **kwargs):
        self.setTCGA(doc)
        self.save(doc)
        return doc
