## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<html>
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
                <div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">${_('Sales Representatives')}</div>
                <div class="act_as_cell" style="width: 170px;background-color:#87CEFA;">${_('Product Category')}</div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${ manager.partner_id.name }</div>
                  <div class="act_as_cell">${ saleperson_name }</div>
                <div class="act_as_cell">${ product_categ.name }</div>
         </div>
         </div>
         <div class="act_as_table list_table" style="margin-top: 10px;">
         <div class="act_as_thead">
         <div class="act_as_row labels">
         <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('MRP Price')}</div>
        <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_(' ')}</div>
        %for i in header:
            <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${i.get('mrp_price') or 0.0}</div>
         %endfor
         <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_(' ')}</div>
        <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_(' ')}</div>
         </div>
        <div class="act_as_row labels">
                                <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('  ')}</div>
                                <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_(' ')}</div>
                                %for i in header:
                                    <div class="act_as_cell" style="width:30px;background-color:#FFFFE0;">${i.get('default_code') or 0.0}</div>
                                 %endfor
                                 <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Pcs')}</div>
                                <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_('Values')}</div>
                            </div> 
                        
                            <div class="act_as_row labels">
                                <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('Stockiest')}</div>
                                <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('Pcs / Cs')}</div>
                                %for i in header:
                                    <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${i.get('case_qty') or 0.0}</div>
                                 %endfor
                                 <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_(' ')}</div>
                                <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_(' ')}</div>
                            </div> 
                      
                            <div class="act_as_row labels">
                                <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_(' Name ')}</div>
                                <div class="act_as_cell" style="width: 50px;background-color:#FFFFE0;">${_('Price')}</div>
                                %for i in header:
                                    <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${i.get('invoice_price') or 0.0}</div>
                                 %endfor
                                 <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_(' ')}</div>
                                <div class="act_as_cell" style="width: 30px;background-color:#FFFFE0;">${_(' ')}</div>
                            </div>                  
         </div> 
         
          %for line in stockiest_line:
          <div class="act_as_tbody">    
              %for cus in line['lines']:    
              <%qty1=0%>
              <%qty2=0%>
              <%qty3=0%>
              <%qty4=0%>
              <%qty5=0%>
              <%qty6=0%>
              <%qty7=0%>
              <%qty8=0%>
             <div class="act_as_row lines">  
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${line.get('name') or ' '}</div>
                   <div class="act_as_cell" style="width: 50px;text-align:left;">${month[0].get('last') or ' '}</div>
                   <%val1=0%>
                   %if cus['lastyr'] != []:                       
                       <%v=0%>
                       %for p in cus['lastyr']:  
                       <%                       
                            qty1 += p.get('amount') or 0
                       %>   
                       %if p.get('amount') != None and p.get('val') != None:
                       <% v =   p.get('amount')  * p.get('val')  %>
                       %endif
                       <% val1+=v%>      
                       <div class="act_as_cell"  style="width: 30px;">${p.get('amount') or 0}</div>
                       %endfor
                    %elif  cus['lastyr'] == []:
                        <div class="act_as_cell"  style="width: 30px;">${_('0')}</div>            
                    %endif
             <div class="act_as_cell"  style="width: 30px;">${formatLang(qty1) or 0 }</div>
             <div class="act_as_cell"  style="width: 30px;">${formatLang(val1) or 0 }</div>
             </div>
             <div class="act_as_row lines">  
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${_(' ')}</div>
                   <div class="act_as_cell" style="width: 50px;text-align:left;">${month[0].get('this') or ' '}</div>
                   <%val1=0%>
                   %if cus['thisyr'] != []:
                       
                       <%v=0%>
                       %for q in cus['thisyr']: 
                       <%                       
                            qty2 += q.get('amount') or 0
                       %>      
                      %if q.get('amount') != None and q.get('val') != None:
                       <% v =   q.get('amount')  * q.get('val')  %>
                       %endif
                       <% val1+=v%>                  
                       <div class="act_as_cell"  style="width: 30px;">${q.get('amount') or 0}</div>
                       %endfor
                    %elif  cus['thisyr'] == []:   
                          <div class="act_as_cell"  style="width: 30px;">${_('0')}</div>
                    %endif
                   <div class="act_as_cell"  style="width: 30px;">${ formatLang(qty2) | amount }</div>
             <div class="act_as_cell"  style="width: 30px;">${formatLang(val1) or 0 }</div>
             </div>
             <div class="act_as_row lines">  
                   <div class="act_as_cell" style="width: 50px;text-align:left;">${_(' ')}</div>
                   <div class="act_as_cell" style="width: 50px;text-align:left;">${_('Opening Stock')}</div>
                    <%val1=0%>
                   %if cus['saleopen'] !=[]:
                      
                       <%v=0%>
                       %for r in cus['saleopen']:                 
                       <%                       
                            qty3 += r.get('amount') or 0
                       %>                       
                       %if r.get('amount') != None and r.get('val') != None:
                       <% v =   r.get('amount')  * r.get('val')  %>
                       %endif
                       <% val1+=v%>      
                       <div class="act_as_cell"  style="width: 30px;">${r.get('amount') or 0}</div>
                       %endfor  
                    %elif cus['saleopen'] ==[]:
                                            <div class="act_as_cell"  style="width: 30px;">${_('0')}</div>
                    %endif   
                   <div class="act_as_cell"  style="width: 30px;">${ formatLang(qty3) | amount }</div>
             <div class="act_as_cell"  style="width: 30px;">${formatLang(val1) or 0 }</div>
             </div>
              <div class="act_as_row lines">  
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${_(' ')}</div>
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${_('Till Date AWD')}</div>
                    <%val1=0%>
                    %if cus['awd'] !=[]:
                       
                       <%v=0%>
                        %for s in cus['awd']:                  
                       <%                       
                            qty4 += s.get('amount') or 0
                       %>        
                       %if s.get('amount') != None and s.get('val') != None:
                       <% v =   s.get('amount')  * s.get('val')  %>
                       %endif
                       <% val1+=v%>                                         
                        <div class="act_as_cell"  style="width: 30px;">${s.get('amount') or 0}</div>
                        %endfor
                    %elif cus['awd'] == []:
                         <div class="act_as_cell"  style="width: 30px;">${_('0')}</div>
                    %endif  
                    <div class="act_as_cell"  style="width: 30px;">${ formatLang(qty4) | amount }</div>    
                    <div class="act_as_cell"  style="width: 30px;">${formatLang(val1) or 0 }</div>                
             </div>            
             <div class="act_as_row lines"> 
                   <div class="act_as_cell" style="width: 50px;text-align:left;">${_(' ')}</div>
                   <div class="act_as_cell" style="width: 50px;text-align:left;">${_('LM RD Till Date')}</div>
                   <%val1=0%>
                   %if cus['rdlast'] != []:
                       
                       <%v=0%>
                       %for tt in cus['rdlast']:  
                       <%                       
                            qty5 += tt.get('amount') or 0
                       %>                                       
                        %if tt.get('amount') != None and tt.get('val') != None:
                       <% v =   tt.get('amount')  * tt.get('val')  %>
                       %endif
                       <% val1+=v%>                            
                       <div class="act_as_cell"  style="width: 30px;">${tt.get('amount') or 0}</div>
                       %endfor  
                   %elif cus['rdlast'] == []:
                                           <div class="act_as_cell"  style="width: 30px;">${_('0')}</div>
                    %endif
                   <div class="act_as_cell"  style="width: 30px;">${ formatLang(qty5) | amount }</div>
              <div class="act_as_cell"  style="width: 30px;">${formatLang(val1) or 0 }</div>                    
            </div>
             <div class="act_as_row lines">  
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${_(' ')}</div>
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${_('TM RD Till Date')}</div>
                   <%val1=0%>
                   %if cus['rdthis'] != []:
                       
                       <%v=0%>
                       %for s in cus['rdthis']:    
                       <%                       
                            qty6+= s.get('amount') or 0
                       %>    
                      %if s.get('amount') != None and s.get('val') != None:
                       <% v =   s.get('amount')  * s.get('val')  %>
                       %endif
                       <% val1+=v%>                                        
                        <div class="act_as_cell"  style="width: 30px;">${s.get('amount') or 0}</div>
                        %endfor
                    %elif cus['rdthis'] == []:
                                            <div class="act_as_cell"  style="width: 30px;">${_('0')}</div>
                    %endif
                    <div class="act_as_cell"  style="width: 30px;">${ formatLang(qty6) | amount }</div>
                <div class="act_as_cell"  style="width: 30px;">${formatLang(val1) or 0 }</div>    
             </div>
             <div class="act_as_row lines">  
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${_(' ')}</div>
                    <div class="act_as_cell" style="width: 50px;text-align:left;">${_('% VS LM')}</div>
                    <%val1=0%>
                    %if cus['percentage'] !=[]:

                       <%v=0%>
                        %for s in cus['percentage']:      
                       <%                       
                            qty7 += s.get('amount') or 0
                       %>    
                       %if s.get('amount') != None and s.get('val') != None:
                       <% v =   s.get('amount')  * s.get('val')  %>
                       %endif
                       <% val1+=v%>                                      
                        <div class="act_as_cell"  style="width: 30px;">${s.get('amount') or 0}</div>
                         %endfor
                   %elif cus['percentage'] ==[]:
                                           <div class="act_as_cell"  style="width: 30px;">${_('0')}</div>
                    %endif
                    <div class="act_as_cell"  style="width: 30px;">${ formatLang(qty7) | amount }</div>                   
                    <div class="act_as_cell"  style="width: 30px;">${formatLang(val1) or 0 }</div>                   
             </div>
             <div class="act_as_row lines">  
                    <div class="act_as_cell" style="width: 50px;text-align:left;border-bottom:1px solid black;">${_(' ')}</div>
                    <div class="act_as_cell" style="width: 50px;text-align:left;border-bottom:1px solid black;">${_('Closing')}</div>
                   <%val1=0%>
                   %if cus['closing'] != []:                       
                       <%v=0%>
                        %for s in cus['closing']:   
                       <%                       
                            qty8 += s.get('amount') or 0
                       %>  
                      %if s.get('amount') != None and s.get('val') != None:
                       <% v =   s.get('amount')  * s.get('val')  %>
                       %endif
                       <% val1+=v%>                                        
                        <div class="act_as_cell"  style="width: 30px;border-bottom:1px solid black;">${s.get('amount') or 0}</div>
                        %endfor
                    %elif cus['closing'] == []:
                        <div class="act_as_cell"  style="width: 30px;border-bottom:1px solid black;">${_('0')}</div>
                    %endif
                    <div class="act_as_cell"  style="width: 30px;border-bottom:1px solid black;">${ formatLang(qty8) | amount }</div>
                    <div class="act_as_cell"  style="width: 30px;border-bottom:1px solid black;">${formatLang(val1) or 0 }</div>
             </div>
         
        
%endfor 
 </div>   
%endfor
</div>                
</body>
</html>
