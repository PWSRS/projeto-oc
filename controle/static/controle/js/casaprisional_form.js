// Cascata para casa prisional
$('#id_casa_prisional').on('change', function() {
    var casaId = $(this).val();
    if (!casaId) {
        // Limpa dependentes se vazio
        $('#id_pavilhao, #id_galeria, #id_cela, #id_alojamento').val(null).trigger('change');
        return;
    }

    $.get(`/ajax/pavilhoes/?casa_id=${casaId}`)
        .done(function(data) {
            var pavilhaoSelect = $('#id_pavilhao');
            pavilhaoSelect.empty().append('<option value="">---------</option>');
            $.each(data, function(index, p) {
                pavilhaoSelect.append(`<option value="${p.id}">${p.nome}</option>`);
            });
            // Destrói e reinicia Select2
            if (pavilhaoSelect.hasClass('select2-hidden-accessible')) {
                pavilhaoSelect.select2('destroy');
            }
            initSelect2('#id_pavilhao');

            // Limpa e reinicia dependentes
            $('#id_galeria, #id_cela, #id_alojamento').empty().append('<option value="">---------</option>').val(null).trigger('change');
            initSelect2('#id_galeria');
            initSelect2('#id_cela');
            initSelect2('#id_alojamento');
        })
        .fail(function() {
            console.error('Erro ao carregar pavilhões');
            alert('Erro ao carregar pavilhões. Tente novamente.');
        });
});

// Cascata para pavilhão (similar)
$('#id_pavilhao').on('change', function() {
    var pavilhaoId = $(this).val();
    if (!pavilhaoId) {
        $('#id_galeria, #id_cela, #id_alojamento').val(null).trigger('change');
        return;
    }

    $.get(`/ajax/galerias/?pavilhao_id=${pavilhaoId}`)
        .done(function(data) {
            var galeriaSelect = $('#id_galeria');
            galeriaSelect.empty().append('<option value="">---------</option>');
            $.each(data, function(index, g) {
                galeriaSelect.append(`<option value="${g.id}">${g.nome}</option>`);
            });
            // Destrói e reinicia
            if (galeriaSelect.hasClass('select2-hidden-accessible')) {
                galeriaSelect.select2('destroy');
            }
            initSelect2('#id_galeria');

            // Limpa e reinicia
            $('#id_cela, #id_alojamento').empty().append('<option value="">---------</option>').val(null).trigger('change');
            initSelect2('#id_cela');
            initSelect2('#id_alojamento');
        })
        .fail(function() {
            console.error('Erro ao carregar galerias');
            alert('Erro ao carregar galerias. Tente novamente.');
        });
});

// Validação Bootstrap (unificada em jQuery)
$('.needs-validation').on('submit', function(event) {
    if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    $(this).addClass('was-validated');
});
});