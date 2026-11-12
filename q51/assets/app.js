
document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('[data-suggestion]').forEach(el=>{const k='nfl2-q51-review-'+el.dataset.suggestion;el.checked=localStorage.getItem(k)==='1';el.addEventListener('change',()=>localStorage.setItem(k,el.checked?'1':'0'));});});
