import os
from cudatext import *
import cudatext as ct
import cudatext_cmd as cmds
import json

from cudax_lib import get_translation
_ = get_translation(__file__) # I18N

JSON_FN = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_find_replace_pairs.json')

class Command:

    def list(self):
        items, items_ = self.get_items()
        if len(items_) > 0:
            w, h = self.get_w_h()
            res = dlg_menu(DMENU_LIST, items, 0, _('Pairs of Find/Replace'), w = w, h = h)
            if res is not None:
                self.set_fr(items_[res])
        else:
            msg_status(_('No pairs found'))

    def add(self):
        f_, r_, rg_ = self.get_fr()
        if f_ and r_:
            res_ = msg_box(_('Do you really want to add pair of of Find/Replace?'), MB_YESNO + MB_ICONQUESTION)
            if res_ == ID_YES:
                self.save_json({
                    'find': f_,
                    'replace': r_,
                    'regex': rg_,
                })
        else:
            msg_box(_('Please fill pair of Find/Replace'), MB_OK)

    def remove(self):
        items, items_ = self.get_items()
        if len(items_) > 0:
            w, h = self.get_w_h()
            res = dlg_menu(DMENU_LIST, items, 0, _('Delete of pairs of Find/Replace'), w = w, h = h)
            if res is not None:
                res_ = msg_box(_('Do you really want to remove pair?'), MB_YESNO + MB_ICONQUESTION)
                if res_ == ID_YES:
                    data = self.load_json()
                    data.pop(res)
                    self.save_json(data, True)
        else:
            msg_status(_('No pairs found'))

    def load_json(self):
        data = ''
        if os.path.exists(JSON_FN):
            with open(JSON_FN, encoding = 'utf-8') as f:
                data = json.load(f)

        return data

    def save_json(self, json_data, update = False):
        if update:
            data = json_data
        else:
            data = self.load_json()
            if data:
                data.append(json_data)
            else:
                data = [json_data]
        with open(JSON_FN, mode = 'w', encoding = 'utf-8') as f:
            json.dump(data, f, indent = 2)

        msg_status(_('Pairs of Find/Replace updated'))

    def get_w_h(self):
        w_ = 600
        h_ = 600
        r = app_proc(PROC_COORD_MONITOR, 0)
        if r:
            w_ = (r[2] - r[0]) // 3
            h_ = (r[3] - r[1]) // 3

        return w_, h_

    def get_items(self):
        items = ''
        items_ = []
        data = self.load_json()
        if data:
            for i in data:
                j = json.loads(json.dumps(i))
                items_.append(j)
                if j['regex']:
                    items += '(.*) '
                items += j['find'] + ' => ' + j['replace'] + "\n"
        else:
            msg_box(_('No pairs found'), MB_OK)

        return items, items_

    def get_fr(self):
        ed.cmd(cmds.cmd_DialogReplace)
        fr_ = app_proc(PROC_GET_FINDER_PROP, '')
        f_ = fr_.get('find_d', [])
        r_ = fr_.get('rep_d' , [])
        rg_ = fr_.get('op_regex_d' , [])

        return f_, r_, rg_

    def set_fr(self, vals):
        ed.cmd(cmds.cmd_DialogReplace)
        app_proc(PROC_SET_FINDER_PROP, dict(
            find_d = vals['find'],
            rep_d = vals['replace'],
            op_regex_d = vals['regex'],
        ))