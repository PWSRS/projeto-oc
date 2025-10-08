$(document).ready(function() {
    // Referências aos selects
    const casaSelect = $('#id_casa_prisional');
    const pavilhaoSelect = $('#id_pavilhao');
    const galeriaSelect = $('#id_galeria');
    const celaSelect = $('#id_cela');
    const alojamentoSelect = $('#id_alojamento');
    
    // Referência ao campo RG/CPF
    const rgCpfInput = $('#id_rg_cpf');

    // =========================================================
    // VARIÁVEIS PARA MODO DE EDIÇÃO
    // CORREÇÃO ESSENCIAL: Armazena os valores originais ANTES de qualquer limpeza.
    // Usaremos essas variáveis para re-selecionar o valor após o AJAX.
    // =========================================================
    let initialPavilhao = pavilhaoSelect.val();
    let initialGaleria = galeriaSelect.val();
    let initialCela = celaSelect.val();
    let initialAlojamento = alojamentoSelect.val();

    // =========================================================
    // LÓGICA DE MÁSCARA CONDICIONAL
    // =========================================================
    function toggleCpfMask() {
        const currentVal = rgCpfInput.val() || '';
        const cleanDigits = currentVal.replace(/\D/g, '');
        
        if (cleanDigits.length === 11) {
            rgCpfInput.mask('000.000.000-00', {reverse: true});
            rgCpfInput.trigger('input'); 
        } else {
            rgCpfInput.unmask();
        }
    }
    
    rgCpfInput.on('input', toggleCpfMask);
    toggleCpfMask(); // Inicializa a máscara na edição
    
    $('form').on('submit', function(event) {
        event.preventDefault();
        const form = $(this);
        // Limpa a máscara antes de enviar
        const valorLimpo = rgCpfInput.val().replace(/\D/g, '');
        rgCpfInput.val(valorLimpo); 
        rgCpfInput.unmask();
        form.off('submit').submit(); // Envia o formulário
    });
    // Fim da lógica de Máscara Condicional

    // =========================================================
    // LÓGICA DE DEPENDÊNCIA DOS SELECTS
    // =========================================================
    
    // Função para limpar um select
    function clearSelect(select) {
        select.empty().append('<option value="">---------</option>');
    }

    // Função para controlar visibilidade/desabilitação
    function updateSelectsVisibility(tipo) {
        console.log('Atualizando visibilidade - Tipo:', tipo);
        // Resetar visibilidade e estado
        pavilhaoSelect.prop('disabled', false).parent().show();
        galeriaSelect.prop('disabled', false).parent().show();
        celaSelect.prop('disabled', false).parent().show();
        alojamentoSelect.prop('disabled', false).parent().show();

        if (tipo === 'pavilhao') {
            galeriaSelect.prop('disabled', true).parent().hide();
            celaSelect.prop('disabled', true).parent().hide();
            alojamentoSelect.prop('disabled', true).parent().hide();
            clearSelect(galeriaSelect);
            clearSelect(celaSelect);
            clearSelect(alojamentoSelect);
        } else if (tipo === 'modular') {
            pavilhaoSelect.prop('disabled', true).parent().hide();
            galeriaSelect.prop('disabled', true).parent().hide();
            celaSelect.prop('disabled', true).parent().hide();
            alojamentoSelect.prop('disabled', true).parent().hide();
        } else if (tipo === 'completa') {
            alojamentoSelect.prop('disabled', true).parent().hide(); 
        } else if (tipo === 'intermediaria' || tipo === 'sem_pavilhao') {
            pavilhaoSelect.prop('disabled', true).parent().hide();
            alojamentoSelect.prop('disabled', true).parent().hide(); 
        } else if (tipo === 'apenas_alojamento') {
            pavilhaoSelect.prop('disabled', true).parent().hide();
            galeriaSelect.prop('disabled', true).parent().hide();
            celaSelect.prop('disabled', true).parent().hide();
        } else {
            alojamentoSelect.prop('disabled', true).parent().hide();
        }
    }

    // Evento ao mudar casa prisional
    casaSelect.on('change', function() {
        const casaId = $(this).val();
        console.log('Casa selecionada:', casaId);

        // Usamos as variáveis iniciais salvas no ready
        const valPavilhao = initialPavilhao;
        const valGaleria = initialGaleria;
        const valCela = initialCela;
        const valAlojamento = initialAlojamento;
        
        // Limpa todos os selects dependentes
        clearSelect(pavilhaoSelect);
        clearSelect(galeriaSelect);
        clearSelect(celaSelect);
        clearSelect(alojamentoSelect);
        
        if (!casaId) {
            console.log('Nenhuma casa selecionada, aplicando padrão completa');
            updateSelectsVisibility('completa');
            return;
        }

        // Busca tipo de estrutura
        fetch(`/ajax/tipo_estrutura/?casa_id=${casaId}`)
            .then(response => {
                if (!response.ok) throw new Error(`Erro HTTP em tipo_estrutura: ${response.status}`);
                return response.json();
            })
            .then(data => {
                const tipo = data.tipo_estrutura || 'completa';
                console.log('Tipo de estrutura retornado:', tipo);
                updateSelectsVisibility(tipo);

                if (tipo === 'pavilhao' || tipo === 'completa') {
                    console.log('Carregando pavilhões para casa_id:', casaId);
                    // Carrega pavilhões
                    fetch(`/ajax/pavilhoes/?casa_id=${casaId}`)
                        .then(response => {
                            if (!response.ok) throw new Error(`Erro HTTP em pavilhões: ${response.status}`);
                            return response.json();
                        })
                        .then(pavilhoes => {
                            console.log('Pavilhôes recebidos:', pavilhoes);
                            if (pavilhoes.length === 0) {
                                console.warn('Nenhum pavilhão encontrado para casa_id:', casaId);
                                pavilhaoSelect.append('<option value="">Nenhum pavilhão disponível</option>');
                            } else {
                                pavilhoes.forEach(p => pavilhaoSelect.append(`<option value="${p.id}">${p.nome}</option>`));
                                // Seleciona o valor salvo e limpa a variável inicial
                                pavilhaoSelect.val(valPavilhao);
                                initialPavilhao = null; 

                                // Dispara o change para carregar o próximo nível (galeria/cela)
                                if (valPavilhao) {
                                    pavilhaoSelect.trigger('change');
                                }
                            }
                            console.log('Pavilhôes carregados:', pavilhoes.length);
                        })
                        .catch(err => {
                            console.error('Erro ao carregar pavilhões:', err);
                            pavilhaoSelect.append('<option value="">Erro ao carregar pavilhões</option>');
                        });
                } else if (tipo === 'sem_pavilhao' || tipo === 'intermediaria') {
                    console.log('Carregando galerias e celas para casa_id:', casaId);
                    
                    // CARREGA GALERIAS
                    fetch(`/ajax/galerias_por_casa/?casa_id=${casaId}`)
                        .then(response => response.json())
                        .then(galerias => {
                            console.log('Galerias recebidas:', galerias);
                            if (galerias.length === 0) {
                                galeriaSelect.append('<option value="">Nenhuma galeria disponível</option>');
                            } else {
                                galerias.forEach(g => galeriaSelect.append(`<option value="${g.id}">${g.nome}</option>`));
                                galeriaSelect.val(valGaleria);
                                initialGaleria = null;

                                if (valGaleria) {
                                    galeriaSelect.trigger('change');
                                }
                            }
                            console.log('Galerias carregadas:', galerias.length);
                        })
                        .catch(err => console.error('Erro ao carregar galerias:', err));

                    // CARREGA CELAS
                    fetch(`/ajax/celas_por_casa/?casa_id=${casaId}`)
                        .then(response => response.json())
                        .then(celas => {
                            console.log('Celas recebidas:', celas);
                            if (celas.length === 0) {
                                celaSelect.append('<option value="">Nenhuma cela disponível</option>');
                            } else {
                                celas.forEach(c => celaSelect.append(`<option value="${c.id}">${c.numero}</option>`));
                                celaSelect.val(valCela);
                                initialCela = null;

                                if (valCela) {
                                    celaSelect.trigger('change');
                                }
                            }
                            console.log('Celas carregadas:', celas.length);
                        })
                        .catch(err => console.error('Erro ao carregar celas:', err));
                } else if (tipo === 'apenas_alojamento') {
                    console.log('Carregando alojamentos para casa_id:', casaId);
                    // Carrega apenas alojamentos
                    fetch(`/ajax/alojamentos_por_casa/?casa_id=${casaId}`)
                        .then(response => {
                            if (!response.ok) throw new Error(`Erro HTTP em alojamentos: ${response.status}`);
                            return response.json();
                        })
                        .then(alojamentos => {
                            console.log('Alojamentos recebidos:', alojamentos);
                            if (alojamentos.error || alojamentos.length === 0) {
                                console.warn('Nenhum alojamento encontrado para casa_id:', casaId);
                                alojamentoSelect.append('<option value="">Nenhum alojamento disponível</option>');
                            } else {
                                alojamentos.forEach(a => {
                                    const nome = a.nome || 'Alojamento sem nome';
                                    alojamentoSelect.append(`<option value="${a.id}">${nome}</option>`);
                                });
                                // Seleciona o valor salvo e limpa a variável inicial
                                alojamentoSelect.val(valAlojamento);
                                initialAlojamento = null;
                            }
                            console.log('Alojamentos carregados:', alojamentos.length || 0);
                        })
                        .catch(err => {
                            console.error('Erro ao carregar alojamentos:', err);
                            alojamentoSelect.append('<option value="">Erro ao carregar alojamentos</option>');
                        });
                }
            })
            .catch(err => console.error('Erro ao buscar tipo_estrutura:', err));
    });

    // Evento ao mudar pavilhão
    pavilhaoSelect.on('change', function() {
        const pavilhaoId = $(this).val();
        console.log('Pavilhão selecionado:', pavilhaoId);

        // Usa as variáveis iniciais salvas ou nulas se já foram usadas
        const valGaleria = initialGaleria;
        const valCela = initialCela;
        const valAlojamento = initialAlojamento;

        clearSelect(galeriaSelect);
        clearSelect(celaSelect);
        clearSelect(alojamentoSelect);

        if (!pavilhaoId) return;

        fetch(`/ajax/galerias/?pavilhao_id=${pavilhaoId}`)
            .then(response => response.json())
            .then(galerias => {
                console.log('Galerias recebidas:', galerias);
                if (galerias.length === 0) {
                    galeriaSelect.append('<option value="">Nenhuma galeria disponível</option>');
                } else {
                    galerias.forEach(g => galeriaSelect.append(`<option value="${g.id}">${g.nome}</option>`));
                    galeriaSelect.val(valGaleria);
                    initialGaleria = null;
                    
                    if (valGaleria) {
                        galeriaSelect.trigger('change');
                    }
                }
                console.log('Galerias carregadas:', galerias.length);
            })
            .catch(err => console.error('Erro ao carregar galerias:', err));
    });

    // Evento ao mudar galeria
    galeriaSelect.on('change', function() {
        const galeriaId = $(this).val();
        console.log('Galeria selecionada:', galeriaId);

        // Usa as variáveis iniciais salvas ou nulas se já foram usadas
        const valCela = initialCela;
        const valAlojamento = initialAlojamento;

        clearSelect(celaSelect);
        clearSelect(alojamentoSelect);

        if (!galeriaId) return;

        fetch(`/ajax/celas/?galeria_id=${galeriaId}`)
            .then(response => response.json())
            .then(celas => {
                console.log('Celas recebidas:', celas);
                if (celas.length === 0) {
                    celaSelect.append('<option value="">Nenhuma cela disponível</option>');
                } else {
                    celas.forEach(c => celaSelect.append(`<option value="${c.id}">${c.numero}</option>`));
                    celaSelect.val(valCela);
                    initialCela = null;
                    
                    if (valCela) {
                        celaSelect.trigger('change');
                    }
                }
                console.log('Celas carregadas:', celas.length);
            })
            .catch(err => console.error('Erro ao carregar celas:', err));
    });

    // Evento ao mudar cela (Este evento parece carregar alojamentos pela CASA, não pela cela. Mantido como está.)
    celaSelect.on('change', function() {
        const casaId = casaSelect.val();
        const celaId = $(this).val(); // A celaId não é usada no fetch, apenas no console.
        console.log('Cela selecionada:', celaId);

        // Usa a variável inicial salva ou nula se já foi usada
        const valAlojamento = initialAlojamento;
        
        clearSelect(alojamentoSelect);

        if (!celaId) return;

        fetch(`/ajax/alojamentos_por_casa/?casa_id=${casaId}`)
            .then(response => response.json())
            .then(alojamentos => {
                console.log('Alojamentos recebidos:', alojamentos);
                if (alojamentos.error || alojamentos.length === 0) {
                    console.warn('Nenhum alojamento encontrado para cela_id:', celaId);
                    alojamentoSelect.append('<option value="">Nenhum alojamento disponível</option>');
                } else {
                    alojamentos.forEach(a => {
                        const nome = a.nome || 'Alojamento sem nome';
                        alojamentoSelect.append(`<option value="${a.id}">${nome}</option>`);
                    });
                    alojamentoSelect.val(valAlojamento);
                    initialAlojamento = null;
                }
                console.log('Alojamentos carregados:', alojamentos.length || 0);
            })
            .catch(err => {
                console.error('Erro ao carregar alojamentos:', err);
                alojamentoSelect.append('<option value="">Erro ao carregar alojamentos</option>');
            });
    });

    // =========================================================
    // INICIALIZAÇÃO PARA MODO DE EDIÇÃO (DISPARA A CASCATA)
    // =========================================================
    if (casaSelect.val()) {
        console.log('Inicializando modo de edição com casa:', casaSelect.val());
        casaSelect.trigger('change');
    }
});