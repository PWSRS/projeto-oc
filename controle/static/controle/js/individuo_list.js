document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const form = document.querySelector('.d-flex');
    
    // 1. Damos um ID ao input para o JS encontrar ele facilmente
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // Se o valor do campo de busca estiver vazio (após remover espaços)
            if (this.value.trim() === '') {
                // Limpa o formulário e envia (ou simplesmente redireciona)
                
                // Opção mais simples: Envia o formulário com o campo vazio
                // A sua View já sabe tratar o campo vazio, retornando a lista completa.
                //form.submit();
                
                // OU, se você quiser apenas garantir que a URL volte ao estado base:
                window.location.href = window.location.pathname; 
            }
        });
    }
});