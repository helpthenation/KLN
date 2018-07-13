## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<html>
## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <%setLang(user.lang)%>
        <center><div class="header"><center>RD Claim - REPORT</center></div> </center>
<div class="act_as_table data_table" style="width: 1100px;">
	<div class="act_as_row labels">
		<div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">${_('Sales Manager')}</div>

		<div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">${_('Sales Representatives')}</div>
		<div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">${_('Product Category')}</div>
	</div>
	<div class="act_as_row">
		<div class="act_as_cell">${ manager.partner_id.name }</div>

		<div class="act_as_cell">${ saleperson_name }</div>
		<div class="act_as_cell">${ product_categ.name }</div>
	</div>
</div>

%for line in partner_lines:                  
<div class="act_as_table list_table" style="margin-top: 10px;">
	<div class="act_as_thead">
		<div class="act_as_row labels">
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('Stockiest Name')}</div>
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('Product Code')}</div>
			%for i in product:
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${i.get('default_code') or ' '}</div>
			%endfor
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Total')}</div>
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Special')}</div>
		</div> 
		<div class="act_as_row labels">
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('  ')}</div>
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('MRP Price')}</div>
			%for i in product:
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${i.get('mrp_price') or 0.0}</div>
			%endfor
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Claim')}</div>
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Pool')}</div>
		</div>                     
		<div class="act_as_row labels">
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_(' ')}</div>
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_(' Invoice Price')}</div>
			%for i in product:
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${i.get('invoice_price') or 0.0}</div>
			%endfor
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Value')}</div>
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('value')}</div>
		</div>                   
		<div class="act_as_row labels">
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_(' ')}</div>
			<div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_(' Scheme Price')}</div>
			%for i in product:
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${i.get('scheme_price') or 0.0}</div>
			%endfor
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Rs.')}</div>
			<div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Rs.')}</div>
		</div> 
	</div>
  <div class="act_as_tbody">
	%for cus in line['customer_details']:
		<%qty=0%>
		<%sqty=0%>

		<div class="act_as_row lines">
			<div class="act_as_cell" style="width: 50px;text-align:left;">${cus.get('name') or ''}</div>
			<div class="act_as_cell" style="width: 50px;text-align:left;">${cus.get('city') or ''}</div>
			%for prod in cus['product_list']:                              
			<%                       
			qty += prod.get('quantity') or 0.0
			%>
			<div class="act_as_cell"  style="width: 20px;">${prod.get('quantity') or 0}</div>
			%endfor                             
			<div class="act_as_cell "  style="width: 20px;background-color:#FFFFE0;">${ formatLang(qty) | amount }</div>
			<div class="act_as_cell "  style="width: 20px;background-color:#FFFFE0;">${cus.get('amount') or 0.0}</div>
		</div>
	%endfor
	<div class="act_as_row lines">
		<div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${line.get('saleperson') or  ' '}</div>
		<div class="act_as_cell "  style="width: 50px;background-color:#FFFFE0;">${line.get('sp_city') or ' '}</div>
		%for nu in line['add']:

		<%sqty += nu.get('sum') or 0.0%>
		<div class="act_as_cell"  style="width: 20px;background-color:#FFFFE0;">${nu.get('sum') or 0}</div>

		%endfor
		<div class="act_as_cell "  style="width: 20px;background-color:#FFFFE0;">${ formatLang(sqty) | amount }</div>
		<div class="act_as_cell "  style="width: 20px;background-color:#FFFFE0;">${line.get('total') or 0.0}</div>	
		</div>  
		</div>
</div> 
%endfor
       
</body>
</html>
