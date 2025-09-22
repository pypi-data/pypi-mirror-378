import inspect

from cryptography.utils import cached_property
from passlib.utils import classproperty

from odoo_commands.utils import create_env


class DataGenerator:
    DEFAULT_USER_PASSWORD = '123'

    populate_params = {
        'usa': 'base.us',
        'russia': 'base.ru',
        'ruble': 'base.RUB',
        # ruble.action_unarchive()

        'russian': 'base.lang_ru',
        # lang_ru.action_unarchive()

        'unit': 'uom.product_uom_unit',
        'main_company': 'base.main_company',
    }

    def __init__(self):
        # self.env = env
        # self.default_user_password = default_user_password
        # self.set_language(lang)
        self._lang = None
        # self.lang = lang
        # self.set_currency(currency)

    @cached_property
    def lang(self):
        if self._lang is not None:
            return self._lang

    @lang.setter
    def lang(self, lang_code):
        # lang = self.env['res.lang'].with_context(active_test=False).search(['code', '=', lang_code])
        lang = self.env.ref(f'base.lang_{lang_code}')
        if not lang.active:
            lang.action_unarchive()
        if self._lang != lang.code:
            context = dict(self.env.context, lang=lang.code)
            self.env = self.env(context=context)
        self._lang = lang.code

    def set_currency(self, code):
        # currency = self.env['res.currency'].with_context(active_test=False).search(['name', '=', code])
        currency = self.env.ref(f'base.{code.upper()}')
        # currency.ensure_one()
        if not currency.active:
            currency.action_unarchive()
        self.currency = currency

    def set_class_records(self):
        self.set_records_by_xml_id(self.attribute_record_xml_ids)

    @classproperty
    def attribute_record_xml_ids(cls):
        xml_ids = {}
        for klass in reversed(cls.__mro__):
            xml = getattr(klass, 'xml', None)
            if xml:
                xml_ids.update(xml)
        return xml_ids

    def set_records_by_xml_id(self, xml_ids):
        for attr_name, xml_id in xml_ids.items():
            if not xml_id:
                continue
            record = self.env.ref(xml_id)
            setattr(self, attr_name, record)

    def account(self, company, code):
        return self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('code', '=', code),
        ]).ensure_one()

    def create_company(self, vals):
        company = self.env['res.company'].create(vals)
        self.env.user.company_ids = [(4, company.id)]

    def execute_settings(self, company, vals):
        self.env['res.config.settings'].with_company(company).create(vals).execute()

    def create_property(self, model_name, field_name, res_id, company, value):
        field = self.env['ir.model.fields']._get(model_name, field_name)
        field_type = self.env[model_name]._fields[field_name].type

        # TODO Make res_id is list of ids
        property_vals = {
            'fields_id': field.id,
            'company_id': company.id,
            'res_id': res_id,
        }

        prop = self.env['ir.property'].search(
            [(name, '=', value) for name, value in property_vals.items()]
        )

        if prop:
            prop.write({
                'value': value,
                'type': field_type,
            })
        else:
            self.env['ir.property'].create(
                dict(property_vals, **{
                    'name': field_name,
                    'value': value,
                    'type': field_type,
                })
            )

    def create_user(self, env, vals, groups=()):
        vals.setdefault('email', vals['login'] + '@example.com')
        vals.setdefault('password', self.DEFAULT_USER_PASSWORD)

        vals.setdefault('company_ids', [(4, vals['company_id'])])

        # TODO Fix ref
        russia = env.ref('base.ru')
        vals.setdefault('country_id', russia.id)
        vals.setdefault('lang', 'ru_RU')
        vals.setdefault('tz', 'Europe/Saratov')

        if not vals.get('groups_id'):
            vals['groups_id'] = [env.ref(xml_id).id for xml_id in groups]

        return env['res.users'].with_context(no_reset_password=True).create(vals)

    def get_populate_param(self, env, name):

        xml_id = self.populate_params.get(name)
        if not xml_id:
            raise LookupError

        record = env.ref(xml_id)
        if record._name in {'res.lang', 'res.currency'}:
            record.action_unarchive()

        return record

    # Main
    def generate(self, database: str):
        env = create_env(database)

        param_values = [
            self.get_populate_param(env, name)
            for name in inspect.signature(self.populate).parameters.keys()
            if name != 'env'
        ]

        records = self.populate(env, *param_values)
        # self.save_refs(records)
        env.cr.commit()

    # def create_env(self, env, lang=lang):
    #     self.env = env
    #     self.default_user_password = default_user_password
    #     self.lang = lang
    #     # self.set_currency(currency)

    def populate(self, env):
        return {}

    def save_refs(self, records):
        import odoo

        if not records:
            return

        ModelData = self.env['ir.model.data']

        for name, value in records.items():
            if not isinstance(value, odoo.models.Model):
                continue

            if len(value) == 1 and not ModelData.search_count([
                ('model', '=', value._name),
                ('res_id', '=', value.id),
            ]):
                ModelData.create({
                    'module': 'test',
                    'name': name,
                    'model': value._name,
                    'res_id': value.id,
                })

    # def commit(self):
    #     self.env.cr.commit()
