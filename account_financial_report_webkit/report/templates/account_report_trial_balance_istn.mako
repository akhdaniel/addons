## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            .account_level_1 {
                text-transform: uppercase;
                font-size: 30px;
                background-color:#F0F0F0;
            }

            .account_level_2 {
                font-size: 12px;
                background-color:#F0F0F0;
            }

            .regular_account_type {
                font-weight: normal;
            }

            .view_account_type {
                font-weight: bold;
            }

            .account_level_consol {
                font-weight: normal;
            	font-style: italic;
            }

            ${css}

            .list_table .act_as_row {
                margin-top: 10px;
                margin-bottom: 10px;
                font-size:10px;
            }
        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <%setLang(user.lang)%>

        <%
        initial_balance_text = {'initial_balance': _('Computed'), 'opening_balance': _('Opening Entries'), False: _('No')}
        %>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell">${_('Chart of Account')}</div>
                <div class="act_as_cell">${_('Fiscal Year')}</div>
                <div class="act_as_cell">
                    %if filter_form(data) == 'filter_date':
                        ${_('Dates Filter')}
                    %else:
                        ${_('Periods Filter')}
                    %endif
                </div>
                <div class="act_as_cell">${_('Accounts Filter')}</div>
                <div class="act_as_cell">${_('Target Moves')}</div>
                <div class="act_as_cell">${_('Initial Balance')}</div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${ chart_account.name }</div>
                <div class="act_as_cell">${ fiscalyear.name if fiscalyear else '-' }</div>
                <div class="act_as_cell">
                    ${_('From:')}
                    %if filter_form(data) == 'filter_date':
                        ${formatLang(start_date, date=True) if start_date else u'' }
                    %else:
                        ${start_period.name if start_period else u''}
                    %endif
                    ${_('To:')}
                    %if filter_form(data) == 'filter_date':
                        ${ formatLang(stop_date, date=True) if stop_date else u'' }
                    %else:
                        ${stop_period.name if stop_period else u'' }
                    %endif
                </div>
                <div class="act_as_cell">
                    %if accounts(data):
                        ${', '.join([account.code for account in accounts(data)])}
                    %else:
                        ${_('All')}
                    %endif
                </div>
                <div class="act_as_cell">${ display_target_move(data) }</div>
                <div class="act_as_cell">${ initial_balance_text[initial_balance_mode] }</div>
            </div>
        </div>

        %for index, params in enumerate(comp_params):
            <div class="act_as_table data_table">
                <div class="act_as_row">
                    <div class="act_as_cell">${_('Comparison %s') % (index + 1,)} (${"C%s" % (index + 1,)})</div>
                    <div class="act_as_cell">
                        %if params['comparison_filter'] == 'filter_date':
                            ${_('Dates Filter:')}&nbsp;${formatLang(params['start'], date=True) }&nbsp;-&nbsp;${formatLang(params['stop'], date=True) }
                        %elif params['comparison_filter'] == 'filter_period':
                            ${_('Periods Filter:')}&nbsp;${params['start'].name}&nbsp;-&nbsp;${params['stop'].name}
                        %else:
                            ${_('Fiscal Year :')}&nbsp;${params['fiscalyear'].name}
                        %endif
                    </div>
                    <div class="act_as_cell">${_('Initial Balance:')} ${ initial_balance_text[params['initial_balance_mode']] }</div>
                </div>
            </div>
        %endfor

        <div class="act_as_table list_table" style="margin-top: 20px;">
            <div class="act_as_thead">
                <div class="act_as_row labels">
                    
                    ## code
                    <div class="act_as_cell first_column" style="width: 20px;">${_('Code')}</div>
                    
                    ## account name
                    <div class="act_as_cell" style="width: 80px;">${_('Account')}</div>

                    ## initial balance
                    <div class="act_as_cell" style="width: 60px;">${_('Initial Balance')}</div>

                    ## mutasi
                    <div class="act_as_cell" style="width: 60px;">${_('Mutasi')}</div>

                    ## balance laba rugi
                    <div class="act_as_cell" style="width: 60px;">${_('Laba/Rugi')}</div>

                    ## balance neraca
                    <div class="act_as_cell" style="width: 60px;">${_('Neraca')}</div>
                </div>
            </div>
        </div>

        <div class="act_as_table list_table">        
            <div class="act_as_thead">
                <div class="act_as_row labels">
                    ## code
                    <div class="act_as_cell" style="width: 20px;"> </div>
                    
                    ## account name
                    <div class="act_as_cell" style="width: 80px;"> </div>

                    ## initial balance
                    <div class="act_as_cell" style="width: 30px;">${_('Debit')}</div>
                    <div class="act_as_cell" style="width: 30px;">${_('Credit')}</div>

                    ## mutasi
                    <div class="act_as_cell" style="width: 30px;">${_('Debit')}</div>
                    <div class="act_as_cell" style="width: 30px;">${_('Credit')}</div>

                    ## balance laba rugi
                    <div class="act_as_cell" style="width: 30px;">${_('Debit')}</div>
                    <div class="act_as_cell" style="width: 30px;">${_('Credit')}</div>

                    ## balance neraca
                    <div class="act_as_cell" style="width: 30px;">${_('Debit')}</div>
                    <div class="act_as_cell" style="width: 30px;">${_('Credit')}</div>

                </div> 
            </div>             
            <div class="act_as_tbody">
              
                <%
                last_child_consol_ids = []
                last_level = False
                %>
                %for current_account in objects:
                    <%
                    if not to_display_accounts[current_account.id]:
                        continue

                    comparisons = comparisons_accounts[current_account.id]

                    if current_account.id in last_child_consol_ids:
                        # current account is a consolidation child of the last account: use the level of last account
                        level = last_level
                        level_class = "account_level_consol"
                    else:
                        # current account is a not a consolidation child: use its own level
                        level = current_account.level or 0
                        level_class = "account_level_%s" % (level,)
                        last_child_consol_ids = [child_consol_id.id for child_consol_id in current_account.child_consol_ids]
                        last_level = current_account.level
                    %>
                    
                    <div class="act_as_row lines ${level_class} ${"%s_account_type" % (current_account.type,)}">
                        ## code
                        <div class="act_as_cell first_column">${current_account.code}</div>

                        ## account name
                        <div class="act_as_cell" style="padding-left: ${level * 5}px;">${current_account.name}</div>

                            
                        ## opening balance
                        ## debit
                        <div class="act_as_cell amount">
                            %if init_balance_accounts[current_account.id] >0:
                                ${formatLang(init_balance_accounts[current_account.id]) | amount}
                            %endif
                        </div>
                        ## credit
                        <div class="act_as_cell amount">
                            %if init_balance_accounts[current_account.id] < 0:
                                ${formatLang(-1*init_balance_accounts[current_account.id]) | amount}
                            %endif
                        </div>

                        ## mutasi
                        ## debit                        
                        <div class="act_as_cell amount">${formatLang(debit_accounts[current_account.id]) | amount}</div>
                        ## credit
                        <div class="act_as_cell amount">${formatLang(credit_accounts[current_account.id]) | amount}</div>


                        ## balance laba/rugi debit
                        <div class="act_as_cell amount">
                            %if current_account.user_type.report_type in ['income','expense']:
                                %if balance_accounts[current_account.id] > 0.0:
                                    ${formatLang(balance_accounts[current_account.id]) | amount}
                                %endif
                            %endif
                        </div>

                        ## balance laba/rugi credit
                        <div class="act_as_cell amount">
                            %if current_account.user_type.report_type in ['income','expense']:
                                %if balance_accounts[current_account.id] < 0.0:
                                    ${formatLang(-1 * balance_accounts[current_account.id]) | amount}
                                %endif
                            %endif
                        </div>

                        ## balance neraca debit
                        <div class="act_as_cell amount">
                            %if current_account.user_type.report_type in ['asset','liability']:
                                %if balance_accounts[current_account.id] > 0.0:
                                    ${formatLang(balance_accounts[current_account.id]) | amount}
                                %endif
                            %endif
                        </div>

                        ## balance neraca credit
                        <div class="act_as_cell amount">
                            %if current_account.user_type.report_type in ['asset','liability']:
                                %if balance_accounts[current_account.id] < 0.0:
                                    ${formatLang(-1 * balance_accounts[current_account.id]) | amount}
                                %endif
                            %endif
                        </div>
                    </div>
                    
                %endfor
            </div>

        </div>
    </body>
</html>
