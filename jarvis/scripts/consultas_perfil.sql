-- =====================================
-- CONSULTAS PARA PERFIL PESSOAL - ALEX
-- =====================================

-- 1. VER TODAS AS PREFERÊNCIAS DO UTILIZADOR
SELECT 
    preference_key as 'Categoria',
    preference_value as 'Valor',
    updated_at as 'Última Atualização'
FROM user_preferences 
ORDER BY updated_at DESC;

-- 2. PERFIL COMPLETO FORMATADO
SELECT 
    CASE preference_key
        WHEN 'comida_favorita' THEN '🍕 Comida Favorita'
        WHEN 'bebida_favorita' THEN '🥤 Bebida Favorita'
        WHEN 'musica_favorita' THEN '🎵 Música Favorita'
        WHEN 'artista_favorito' THEN '🎤 Artista Favorito'
        WHEN 'genero_musical' THEN '🎶 Género Musical'
        WHEN 'filme_favorito' THEN '🎬 Filme/Série Favorita'
        WHEN 'cor_favorita' THEN '🎨 Cor Favorita'
        WHEN 'desporto_favorito' THEN '⚽ Desporto Favorito'
        WHEN 'hobby_favorito' THEN '🎯 Hobby Favorito'
        WHEN 'animal_favorito' THEN '🐾 Animal Favorito'
        WHEN 'estacao_favorita' THEN '🌸 Estação Favorita'
        WHEN 'cidade_favorita' THEN '🏙️ Cidade Favorita'
        ELSE CONCAT('📋 ', REPLACE(preference_key, '_', ' '))
    END as 'Preferência',
    preference_value as 'Valor',
    DATE_FORMAT(created_at, '%d/%m/%Y %H:%i') as 'Criado',
    DATE_FORMAT(updated_at, '%d/%m/%Y %H:%i') as 'Atualizado'
FROM user_preferences 
ORDER BY updated_at DESC;

-- 3. MENSAGENS QUE MENCIONAM PREFERÊNCIAS PESSOAIS
SELECT 
    c.title as 'Conversa',
    m.message_type as 'Tipo',
    m.content as 'Conteúdo',
    TIME(m.timestamp) as 'Hora'
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE m.content REGEXP '(favorit|prefir|gost)'
AND DATE(m.timestamp) = CURDATE()
ORDER BY m.timestamp DESC;

-- 4. ESTATÍSTICAS DO PERFIL
SELECT 
    'Total de Preferências' as 'Métrica',
    COUNT(*) as 'Valor'
FROM user_preferences
UNION ALL
SELECT 
    'Categorias Diferentes' as 'Métrica',
    COUNT(DISTINCT preference_key) as 'Valor'
FROM user_preferences
UNION ALL
SELECT 
    'Última Atualização' as 'Métrica',
    DATE_FORMAT(MAX(updated_at), '%d/%m/%Y %H:%i') as 'Valor'
FROM user_preferences;

-- 5. EVOLUÇÃO DAS PREFERÊNCIAS (MUDANÇAS)
SELECT 
    preference_key as 'Categoria',
    preference_value as 'Valor Atual',
    DATE_FORMAT(created_at, '%d/%m/%Y %H:%i') as 'Primeira Vez',
    DATE_FORMAT(updated_at, '%d/%m/%Y %H:%i') as 'Última Mudança',
    CASE 
        WHEN created_at = updated_at THEN 'Nunca mudou'
        ELSE 'Foi atualizada'
    END as 'Status'
FROM user_preferences 
ORDER BY updated_at DESC;

-- 6. CONVERSAS ONDE FORAM DEFINIDAS PREFERÊNCIAS
SELECT 
    c.title as 'Conversa',
    c.created_at as 'Data da Conversa',
    GROUP_CONCAT(DISTINCT up.preference_key) as 'Preferências Definidas',
    COUNT(DISTINCT up.preference_key) as 'Total'
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
JOIN user_preferences up ON DATE(m.timestamp) = DATE(up.created_at)
WHERE m.content REGEXP '(favorit|prefir|gost)'
GROUP BY c.id, c.title, c.created_at
ORDER BY c.created_at DESC;

-- 7. ANÁLISE DE PERSONALIZAÇÃO (QUANTAS VEZES O ALEX USOU O PERFIL)
SELECT 
    DATE(m.timestamp) as 'Data',
    COUNT(CASE WHEN m.message_type = 'user' AND m.content REGEXP '(favorit|prefir|gost)' THEN 1 END) as 'User definiu preferências',
    COUNT(CASE WHEN m.message_type = 'assistant' AND m.content REGEXP '(lembro|sei que|sua.*favorit)' THEN 1 END) as 'Alex usou personalização',
    COUNT(*) as 'Total de mensagens'
FROM messages m
WHERE DATE(m.timestamp) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY DATE(m.timestamp)
ORDER BY DATE(m.timestamp) DESC;

-- 8. PERFIL RESUMO PARA DASHBOARD
SELECT 
    '👤 PERFIL PESSOAL' as 'Secção',
    '' as 'Detalhes'
UNION ALL
SELECT 
    CONCAT('  ', CASE preference_key
        WHEN 'comida_favorita' THEN '🍕'
        WHEN 'bebida_favorita' THEN '🥤'
        WHEN 'musica_favorita' THEN '🎵'
        WHEN 'artista_favorito' THEN '🎤'
        WHEN 'genero_musical' THEN '🎶'
        WHEN 'filme_favorito' THEN '🎬'
        WHEN 'cor_favorita' THEN '🎨'
        WHEN 'desporto_favorito' THEN '⚽'
        WHEN 'hobby_favorito' THEN '🎯'
        WHEN 'animal_favorito' THEN '🐾'
        WHEN 'estacao_favorita' THEN '🌸'
        WHEN 'cidade_favorita' THEN '🏙️'
        ELSE '📋'
    END, ' ', REPLACE(preference_key, '_', ' ')) as 'Secção',
    preference_value as 'Detalhes'
FROM user_preferences
ORDER BY preference_key;

-- 9. ENCONTRAR PADRÕES NAS PREFERÊNCIAS
SELECT 
    'Palavras mais usadas nas preferências:' as 'Análise',
    '' as 'Resultado'
UNION ALL
SELECT 
    'Comum em comidas:',
    GROUP_CONCAT(DISTINCT 
        CASE 
            WHEN preference_value REGEXP '(pizza|hamburguer|massa)' THEN 'Fast Food'
            WHEN preference_value REGEXP '(sushi|sashimi|japones)' THEN 'Culinária Japonesa'
            WHEN preference_value REGEXP '(salada|vegetal|fruta)' THEN 'Saudável'
            ELSE NULL
        END
    ) as 'Resultado'
FROM user_preferences 
WHERE preference_key = 'comida_favorita'
UNION ALL
SELECT 
    'Estilo musical:',
    GROUP_CONCAT(DISTINCT 
        CASE 
            WHEN preference_value REGEXP '(rock|metal)' THEN 'Rock/Metal'
            WHEN preference_value REGEXP '(pop|dance)' THEN 'Pop/Dance'
            WHEN preference_value REGEXP '(jazz|blues)' THEN 'Jazz/Blues'
            WHEN preference_value REGEXP '(classica|erudita)' THEN 'Clássica'
            ELSE NULL
        END
    ) as 'Resultado'
FROM user_preferences 
WHERE preference_key IN ('genero_musical', 'artista_favorito');

-- 10. BACKUP DAS PREFERÊNCIAS (PARA EXPORTAR)
SELECT 
    preference_key,
    preference_value,
    data_type,
    created_at,
    updated_at
FROM user_preferences
ORDER BY preference_key;

-- =====================================
-- VIEWS ÚTEIS (EXECUTAR UMA VEZ)
-- =====================================

-- View para perfil atual
CREATE OR REPLACE VIEW perfil_atual AS
SELECT 
    CASE preference_key
        WHEN 'comida_favorita' THEN '🍕 Comida'
        WHEN 'bebida_favorita' THEN '🥤 Bebida'
        WHEN 'musica_favorita' THEN '🎵 Música'
        WHEN 'artista_favorito' THEN '🎤 Artista'
        WHEN 'genero_musical' THEN '🎶 Género'
        WHEN 'filme_favorito' THEN '🎬 Filme'
        WHEN 'cor_favorita' THEN '🎨 Cor'
        WHEN 'desporto_favorito' THEN '⚽ Desporto'
        WHEN 'hobby_favorito' THEN '🎯 Hobby'
        WHEN 'animal_favorito' THEN '🐾 Animal'
        WHEN 'estacao_favorita' THEN '🌸 Estação'
        WHEN 'cidade_favorita' THEN '🏙️ Cidade'
        ELSE CONCAT('📋 ', REPLACE(preference_key, '_', ' '))
    END as categoria,
    preference_value as valor,
    updated_at as atualizado
FROM user_preferences 
ORDER BY updated_at DESC;

-- View para histórico de personalização
CREATE OR REPLACE VIEW historico_personalizacao AS
SELECT 
    DATE(m.timestamp) as data,
    c.title as conversa,
    m.message_type as tipo,
    CASE 
        WHEN m.content REGEXP '(minha.*favorit|meu.*favorit|gosto de|prefiro)' AND m.message_type = 'user' 
        THEN 'Definiu preferência'
        WHEN m.content REGEXP '(lembro|sei que|sua.*favorit)' AND m.message_type = 'assistant'
        THEN 'Usou personalização'
        ELSE 'Normal'
    END as acao,
    LEFT(m.content, 100) as preview
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE m.content REGEXP '(favorit|prefir|gost|lembro|sei que)'
ORDER BY m.timestamp DESC;