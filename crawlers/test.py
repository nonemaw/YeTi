class MenuFetcher(Fetcher):
    def __init__(self, company: str, jison: Jison = None, db=None,
                 max_repeat: int = 3, sleep_time: int = 0):
        super().__init__(max_repeat, sleep_time)
        self.jison = jison
        self.company = company.lower()
        self.db = db

    def change_db(self, db):
        self.db = db

    def r_dump_interface(self, menu_path: str,
                         session,
                         node_id: str = None,
                         debug: bool = False) -> list:
        """
        get `children` under current `menu_path`

        then acquire `sub_children` for each child in `children`

        `_q` is a queue for thread, indicating method is running as a thread
        """
        interface_header = {
            'Content-Type': 'application/json',
            'referer': f'https://{self.company.lower()}.xplan.iress.com.au/factfind/edit_interface',
        }

        menu_post = {
            "method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
            "params": [{
                "interface_type": "client",
                "menu_path": menu_path
            }],
            "id": 1
        }

        self.jison.load(session.post(f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/',
                                    json=menu_post,
                                    headers=interface_header).json())
        local_children = self.jison.get_object('children', value_only=True)

        children = []
        # loop in `children`, acquire `sub_children` for each child
        for child in local_children:
            if child.get('hidden'):
                continue

            text = child.get('title')
            child_id = child.get('node_id')
            child_path = re.search('client_([0-9_\-]+)', child_id)
            specific_flag = False
            sub_children = []

            if debug:
                print(text)

            # normal node case (id starts with `client_xxx`)
            if child_path:
                child_path = child_path.group(1).replace('-', '/')
                sub_children = self.r_dump_interface(child_path, session)

            # if current child has no child and with a valid leaf id (a leaf)
            if not sub_children and re.search('(.+)_([\d]+_[\d]+)', child_id):
                leaf_type = self.dump_leaf_page(child_id, menu_path, text,
                                                session)
                if leaf_type in ['gap', 'title', 'text']:
                    continue

                children.append({
                    'id': child_id,
                    'text': text,
                    'type': leaf_type
                })
            # if current child has no children but with an invalid leaf id
            elif not sub_children:
                children.append({
                    'id': child_id,
                    'text': text,
                    'type': 'other'
                })
            # else, append `sub_children` to current child
            else:
                children.append({
                    'id': child_id,
                    'text': text,
                    'type': 'root',
                    'children': sub_children
                })

            if specific_flag:
                return children

        else:
            return children

    def dump_leaf_page(self, node_id: str, menu_path: str, text: str,
                       session) -> str:
        interface_header = {
            'Content-Type': 'application/json',
            'referer': f'https://{self.company.lower()}.xplan.iress.com.au/factfind/edit_interface',
        }

        custom_page_name, index = re.search('(.+)_([\d]+_[\d]+)',
                                            node_id).groups()
        subpage_index, field_index = [int(i) for i in index.split('_')]
        leaf_post = {
            "method": "ajax.PageElementSettingAjax_rpc_html_kYjvPyv3_",
            "params": [
                {
                    "custom_page_name": custom_page_name,
                    "interface_type": "client",
                    "menu_path": menu_path,
                    "field_index": field_index,
                    "subpage_index": subpage_index,
                    "element_type": "",
                }
            ],
            "id": 1
        }

        self.jison.load(session.post(f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/',
                                json=leaf_post,
                                headers=interface_header).json())

        leaf_type = self.jison.get_object('title', value_only=True).lower()

        if leaf_type in ['gap', 'title', 'text']:
            return leaf_type

        if leaf_type == 'xplan':
            page_html = self.jison.get_multi_object('html')[2].get('html')
        else:
            page_html = self.jison.get_multi_object('html')[0].get('html')

        page = {}
        soup = BeautifulSoup(page_html, 'html5lib')
        # basic information for each page
        try:
            name = soup.find('option', {'selected': True}).getText()
            if re.findall('\[(.+?)\] (.+)', name):
                name = '--'.join(re.findall('\[(.+?)\] (.+)', name)[0])
        except:
            name = '(Empty)'
        if name == 'no':
            name = '(Empty)'
        if name == 'Client':
            name = text
        content = {'entities': []}

        if soup.find('input', {'checked': True, 'id': 'entity_types_1'}):
            content.get('entities').append('individual')
        if soup.find('input', {'checked': True, 'id': 'entity_types_2'}):
            content.get('entities').append('superfund')
        if soup.find('input', {'checked': True, 'id': 'entity_types_3'}):
            content.get('entities').append('partnership')
        if soup.find('input', {'checked': True, 'id': 'entity_types_4'}):
            content.get('entities').append('trust')
        if soup.find('input', {'checked': True, 'id': 'entity_types_5'}):
            content.get('entities').append('company')
        page['leaf_basic'] = content

        # try to acquire table content if an `xplan` page
        if leaf_type == 'xplan':
            content = {'table1': [], 'table2': []}

            if name.lower() in subgroup_name_ref:
                content['subgroup'] = subgroup_name_ref.get(name.lower())

            table1_method = "ajax.XplanElementListSettingAjax_rpc_html_WEaBDM8__"
            table2_method = "ajax.XplanElementEditSettingAjax_rpc_html_HBm947gH_"
            leaf_post_xtable = {
                "method": None,
                "params": [
                    {
                        "has_partner": False,
                        "domain": "factfind",
                        "guid": "00000000-0000-0000-0000-000000000000",
                        "cover_type": "",
                        "coa_access": False,
                        "entity_type": 0,
                        "locale": "AU",
                        "custom_page_name": "",
                        "editable": False,
                        "subpage_index": 0,
                        "partnerid": 0,
                        "mode": "edit",
                        "extra_params": "",
                        "field_index": 7,
                        "is_partner": False,
                        "entityid": 0,
                        "list_name": "",
                        "element_name": self.jison.get_object('element_name',
                                                         value_only=True),
                        "render_method": "factfind"
                    }
                ],
                "id": 1
            }

            leaf_post_xtable['method'] = table1_method

            self.jison.load(
                session.post(f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/',
                             json=leaf_post_xtable,
                             headers=interface_header).json())

            # if this `xplan` page has list with tabs
            # process table content
            table_html = self.jison.get_object('tabs_html', value_only=True)
            if table_html:
                list_view_html = table_html.get('_above-tabs')
                full_view_html = table_html.get('_hidden-items')

                soup = BeautifulSoup(list_view_html, 'html5lib')
                for td in soup.find_all('td',
                                        {'style': 'white-space: nowrap'}):
                    content.get('table1').append(td.findNext('td').getText())

                soup = BeautifulSoup(full_view_html, 'html5lib')
                for td in soup.find_all('td',
                                        {'style': 'white-space: nowrap'}):
                    content.get('table2').append(td.findNext('td').getText())

            # if this `xplan` page has list with checkbox or empty page
            # process `page_html`
            else:
                for input in soup.find_all('input', {'checked': 'checked',
                                                     'name': 'xstore_listfields'}):
                    content.get('table1').append(
                        input.findNext('label').getText())

                for input in soup.find_all('input', {'checked': 'checked',
                                                     'name': 'xstore_capturefields'}):
                    content.get('table2').append(
                        input.findNext('label').getText())

            if content.get('table1') or content.get('table2'):
                page['leaf_xplan'] = content

        # not an `xplan` page
        else:
            if leaf_type == 'group':
                content = {'group': []}

                for option in soup.find('select',
                                        {'id': 'select_fields_0'}).find_all(
                    'option'):
                    content.get('group').append(option.getText())

                page['leaf_group'] = content

            elif leaf_type == 'field':
                leaf_type = 'variable'

        InterfaceLeafPage(node_id, name, leaf_type, menu_path, page).new(
            specific_db=self.db)

        return leaf_type