# LayerOne
Layer7 é uma ferramenta de linha de comando escrita em Python que decompõe vídeos em quadros individuais, processa cada imagem com FFMPEG aceleração CUDA e realiza upscaling quadro a quadro usando o animefx

```text
       ┌─────────────────┐                                                   
       │                 │                                                   
┌──────┤     Video       │                                                   
│      │                 │                                                   
│      └───────┬─────────┘                                                   
│              │                                                              
│              ▼                                                              
│      ┌────────────────────┐        ┌───────────────────┐           
│      │                    │        │                   │           
│      │ Async Frame img    │        │   Async upscale   │           
│      │ extract (FFMPEG)   ├───────►│      Image        │           
│      │                    │        │                   │           
│      └────────────────────┘        └────────┬──────────┘           
│                                             │                       
│      ┌────────────────────┐                 ▼                       
└─────►│   extract audio    │       ┌────────────────────┐           
       └─────────┬──────────┘       │                    │           
                 │                  │FFMEG merge to video│           
                 ▼                  │                    │           
       ┌────────────────────┐       └─────────┬──────────┘
       │                    │                 │ 
       │       Audio        │                 ▼
       │                    │       ┌────────────────────┐           
       └───────┬────────────┘       │                    │           
               │                    │  video optimized   │           
               │                    │                    │           
               │                    └─────────┬──────────┘           
               │                              │                                     
               │                              ▼                    
               │                   ┌────────────────────┐          
               │                   │                    │          
               └─────────────────► │    Merge data      │
                                   │                    │
                                   └──────────┬─────────┘          
                                              │                     
                                              ▼                     
                                    ┌────────────────────┐         
                                    │ Final video merged │         
                                    └────────────────────┘

```
