A ideia inicial do código era uma (Mostrar imagens enquanto áudio tocava) e foi para outra (Mostrar vídeos satisfatórios com uma legenda enquanto um áudio com música e roteiro tocava), então alguns imports devem estar sem sentido. 	

O código não foi feito para ser compartilhado, e infelizmente isso piora um pouco a compreensão do mesmo (Arquivos como legendaput e vm2gi tão aí pra provar). Mas caso alguém de fora veja ele e tenha ideias para a torna-lo mais legível, por favor, me contacte!

Ele interage com alguns diretórios que não estão presentes aqui, então caso queira usar tal código, aqui eles e sua função:

"roteiros/" - Serve para temporariamente guardar os roteiros que a API criava. Não é tão importante assim agora, mas me ajudou muito para analisar algumas coisas, como a interação dos parâmetros do prompt da API para com o resultado final, independentemente do tema, e como as funções de correção e sincronização do roteiro funcionavam

"audios/" - Serve para temporariamente guardar os áudios que o código criava, tanto o Base (Só roteiro) quanto o com música. Não é necessario também, porém ajudou em análises.

"thumbVideos/" - Serve para guardar os vídeos que serão usados como thumbnaill do vídeo, no caso, a imagem que vai aparecer de capa.

"videosBase/"  - Serve para guardar os vídeos (Majoritariamente curtos e satisfatórios) que aparecerão no vídeo como conteúdo.
