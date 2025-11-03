# 🛰️ Spottler – Monitoramento Inteligente de Ocupação de Restaurantes

> Sistema de análise e monitoramento de ocupação em tempo real, integrando visão computacional (YOLO e LLaMA), backend em FastAPI e frontend em Flutter.  
> Projeto desenvolvido como Trabalho de Conclusão de Curso em Engenharia da Computação – Instituto Mauá de Tecnologia (IMT).

## 📊 Visão Geral

O **Spottler** é uma plataforma inteligente para **monitorar a ocupação de restaurantes em tempo real**, combinando **IA, visão computacional e análise de dados**.  
O sistema foi projetado com uma arquitetura **baseada em microserviços** e foca em oferecer métricas analíticas de fluxo de pessoas, taxa de ocupação e estimativas de tempo médio de permanência.

---

## ⚙️ Arquitetura do Sistema

A arquitetura segue o modelo de **microserviços distribuídos**, integrando back-end em **Python/FastAPI**, banco de dados **MongoDB Atlas**, e **front-end em Flutter**.

### 🔧 Microserviços Principais
 Serviço | Descrição | Tecnologias |
|----------|------------|-------------|
| `auth_service` | Autenticação e registro de usuários | FastAPI, JWT |
| `user_service` | CRUD de usuários | FastAPI, MongoDB |
| `restaurant_service` | Cadastro de restaurantes e ocupação | FastAPI, Pydantic, Async I/O |
| `analytics_service` | Processamento e análise de métricas | FastAPI, Pandas, NumPy |
| `detection_service` | Detecção de pessoas em tempo real (YOLOv8 e LLaMA) | Python, Ultralytics |
| `frontend` | Interface do usuário | Flutter/Dart |

## 🧠 Funcionalidades Principais

- 🧍‍♂️ **Detecção de pessoas** via YOLOv8 (câmeras RTSP ou upload de frames)  
- 📈 **Análise de ocupação e fluxo** em tempo real
- 💾 **Banco de dados em nuvem (MongoDB Atlas)**  
- 🌐 **Deploy completo no Heroku**  
- 📊 **Dashboard analítico com gráficos interativos**
- 🔒 **Autenticação JWT (registro/login de usuários)**

  
