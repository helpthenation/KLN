## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            .overflow_ellipsis {
          
                white-space: nowrap;
            }
            ${css}
        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <%setLang(user.lang)%>
<div class="act_as_table data_table" style="width: 1100px;">
        <div class="act_as_row labels">
            <div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">${_('Sales Manager')}</div>                
            <div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">
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
            <div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">${_('Sales Representatives')}</div>
        </div>
    <div class="act_as_row">
        <div class="act_as_cell">${ manager.partner_id.name }</div>
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
        <div class="act_as_cell">${ saleperson_name }</div>
    </div>
</div>

<div class="act_as_table list_table" style="margin-top: 10px;"> 
<div class="act_as_tbody">
         %for line in consolidate:
                <div class="act_as_row lines">
                    <div class="act_as_cell" style="width: 170px;background-color:#FFFFE0;">${_('Stockiest Name')}</div>
                    <div class="act_as_cell" style="width: 100px;background-color:#FFFFE0;">${_('City')}</div>
                    %for i in categ_name:
                        <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${i.get('name') or ' '}</div>
                     %endfor
                     <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('Total Claim Value')}</div>
                    <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('Special Pool Value')}</div>
                </div>  

              %for cus in line['customer_details']:
                <%qty=0%>
                <%sqty=0%>
                <div class="act_as_row lines">
                       <div class="act_as_cell" style="width: 120px;text-align:left;">${cus.get('name') or ''}</div>
                       <div class="act_as_cell" style="width: 100px;text-align:left;">${cus.get('city') or ''}</div>
                       %for p in cus['prod']:                             
                       <%                       
                        qty += p.get('qty') or 0.0
                        %>
                       <div class="act_as_cell"  style="width: 50px;">${p.get('qty') or 0}</div>
                       %endfor                             
                       <div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${ formatLang(qty) | amount }</div>
                       <div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${cus.get('amount') or 0.0}</div>  
                </div>
               %endfor
             <div class="act_as_row lines">
                 <div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${line.get('saleperson') or  ' '}</div>
                 <div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${line.get('sp_city') or ' '}</div>
                  %for nu in line['categ_count']:
                     
                      <%sqty += nu.get('sum') or 0.0%>
                      <div class="act_as_cell"  style="width: 50px;background-color:#FFFFE0;">${nu.get('sum') or 0}</div>
                      
                  %endfor
                 <div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${ formatLang(sqty) | amount }</div>
                 <div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${line.get('total') or 0.0}</div>
          </div>
<br/>
           %endfor
 </div>
</div>
</body>
</html>
