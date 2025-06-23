# 언론사별 편향성 분석 및 중립 뉴스 추천 시스템

## 📌 프로젝트 개요
한국 언론의 정치적 편향성과 가짜뉴스 문제를 해결하기 위해, 본 프로젝트는 딥러닝 기반 감성 분석 및 정치 성향 분류를 활용하여 언론사별 편향성을 분석하고, 중립적인 관점의 기사를 추천하는 시스템을 개발합니다.

---

## 🎯 목표

1. **언론사별 정치적 편향성 정량화**: 주요 언론사의 정치 성향을 객관적으로 측정
2. **다중 태스크 학습 모델**: 정당 성향 분류와 감성 분석을 동시에 수행하는 통합 모델 개발
3. **중립성 기반 뉴스 추천**: 사용자 관심 키워드에 대한 중립적 관점의 기사 추천
4. **자동화된 뉴스 요약**: 다중 출처 기사를 통합하여 객관적 요약 제공

---

## 🧪 연구 방법

### 1. 데이터 수집 및 전처리
- **크롤링 시스템**: Selenium 기반 네이버 뉴스 크롤러 (`crawling/naver_news_crawler.py`)
  - 40개 이상 주요 언론사 지원 (신문사, 방송사, 통신사)
  - 정치 섹션 기사 자동 필터링
  - 헤드리스 모드로 안정적인 데이터 수집
- **전처리 파이프라인**: (`preprocess/news_preprocessing.ipynb`)
  - HTML 태그 및 불필요한 텍스트 제거
  - 기자명, 언론사명, 저작권 문구 정리
  - 중복 기사 제거 및 텍스트 정규화

### 2. 베이스라인 모델 (`model/baseline_model.ipynb`)
- **TF-IDF + Logistic Regression** 기반 기본 성능 측정
- **정당 성향 분류**: 국민의힘(0), 민주당(1), 그외(2)
- **성능**: F1-score 0.6406, 정확도 0.6439

### 3. 다중 태스크 딥러닝 모델 (`model/multitask_model.ipynb`)
- **모델 아키텍처**: 
  - BERT 기반 인코더 (`klue/roberta-base` 사전학습 모델)
  - BiLSTM 레이어로 문맥 정보 강화
  - 정당 분류기 + 감성 분류기 (긍정/중립/부정)
- **특징**:
  - 클래스 불균형 해결을 위한 가중 손실 함수
  - Early Stopping 및 Learning Rate Scheduling
  - 멀티태스크 학습으로 모델 효율성 향상
- **사전학습 모델**: `klue/roberta-base` (한국어 RoBERTa)

### 4. Longformer 확장 모델 (`model/multitask_model_longformer.ipynb`)
- **긴 텍스트 처리**: 최대 4096 토큰까지 처리 가능
- **문서 수준 분석**: 전체 기사 내용을 고려한 편향성 분석
- **사전학습 모델**: `allenai/longformer-base-4096` (긴 문서 처리용)

### 5. 뉴스 요약 및 추천 시스템 (`summarization/1. sbert_based_generative.ipynb`)
- **키워드 기반 필터링**: 사용자 관심 키워드로 관련 기사 추출
- **SBERT 임베딩**: `snunlp/KR-SBERT-V40K-klueNLI-augSTS` 모델 사용
- **클러스터링**: K-means로 유사 기사 그룹화
- **중립성 기반 추천**: 편향성 점수를 고려한 기사 순위화
- **자동 요약**: `digit82/kobart-summarization` 모델로 기사 요약 생성

### 6. 편향성 지수 통합 분석 (`model/통합 편향성 지수.ipynb`)
- **종합 편향성 지표**: 정당 성향 + 감성 분석 결과 통합
- **언론사별 비교 분석**: 객관적 편향성 측정 지표 제공

---

## 🗓️ 프로젝트 진행 상황

| 단계 | 상태 | 완료 내용 |
|------|------|-----------|
| 1주차 | ✅ 완료 | 주제 확정, 네이버 뉴스 크롤러 개발 |
| 2주차 | ✅ 완료 | 데이터 수집 (85,698개 기사), 전처리 파이프라인 구축 |
| 3주차 | ✅ 완료 | 베이스라인 모델 구현, 다중 태스크 모델 개발 |
| 4주차 | ✅ 완료 | Longformer 확장, 뉴스 요약 시스템 구현 |
| 5주차 | ✅ 완료 | 통합 편향성 지수 분석, 최종 결과 정리 |

---

## 🌟 주요 성과

### 기술적 성과
- **대규모 데이터 처리**: 85,698개 정치 기사 수집 및 전처리
- **다중 태스크 학습**: 정당 성향 + 감성 분석 동시 수행 모델
- **실시간 크롤링**: 안정적인 뉴스 데이터 수집 시스템
- **한국어 특화**: 한국어 SBERT 모델을 활용한 고품질 임베딩

### 분석 결과
- **언론사별 편향성 정량화**: 객관적 편향성 측정 지표 개발
- **중립 뉴스 추천**: 편향성 점수 기반 기사 추천 알고리즘
- **자동 요약 시스템**: 다중 출처 기사 통합 요약 기능

---

## ⚠️ 한계점 및 향후 발전 방향

### 현재 한계점
- **레이블링 주관성**: 수작업 레이블링의 개인적 편향 가능성
- **모델 성능**: 복잡한 정치적 맥락 완전 포착의 어려움
- **실시간성**: 실시간 뉴스 업데이트 반영의 제한

### 향후 발전 방향
- **자동 레이블링**: 대규모 언어 모델을 활용한 자동 레이블링
- **실시간 분석**: 실시간 뉴스 편향성 분석 시스템 구축
- **개인화 추천**: 사용자 선호도 기반 맞춤형 뉴스 추천
- **댓글 분석**: 댓글 데이터를 활용한 종합적 편향성 분석
- **다국어 지원**: 영어, 중국어 등 다국어 뉴스 분석 확장

---

## 🛠️ 기술 스택

### 백엔드 & 데이터 처리
- **언어**: Python 3.8+
- **데이터 처리**: Pandas 2.1.0, NumPy 1.24.3
- **웹 크롤링**: Selenium, BeautifulSoup
- **텍스트 전처리**: KoNLPy, 정규표현식

### 머신러닝 & 딥러닝
- **프레임워크**: PyTorch 2.0.1, Transformers 4.31.0
- **모델**: 
  - 한국어 BERT (`klue/roberta-base`) - 다중 태스크 학습
  - Longformer (`allenai/longformer-base-4096`) - 긴 텍스트 처리
  - KR-SBERT (`snunlp/KR-SBERT-V40K-klueNLI-augSTS`) - 문장 임베딩
  - KoBART (`digit82/kobart-summarization`) - 한국어 요약
- **평가**: Scikit-learn 1.3.0, F1-score, 정확도

### 시각화 & 분석
- **시각화**: Matplotlib 3.7.2, Seaborn 0.12.2
- **클러스터링**: K-means, Silhouette Score
- **진행률**: TQDM 4.65.0

---

## 📂 프로젝트 구조

```
News_Bias_Analysis/
├── crawling/                               # 뉴스 크롤링 시스템
│   ├── naver_news_crawler.py               # 네이버 뉴스 크롤러
│   ├── run_crawler.py                      # 크롤러 실행 스크립트
│   └── requirements.txt                    # 크롤링 관련 의존성
├── preprocess/                             # 데이터 전처리
│   ├── news_preprocessing.ipynb            # 텍스트 전처리
│   ├── news_sentiment_label.ipynb          # 감성 레이블링
│   └── SentiWord_Dict.txt                  # 감성 사전
├── kappa/                                  # 평가 지표
│   ├── kappa.ipynb                         # Kappa 계수 계산
│   └── 케파통계 - Sheet1.csv                # 평가 데이터
├── model/                                  # 딥러닝 모델
│   ├── baseline_model.ipynb                # TF-IDF 베이스라인
│   ├── multitask_model.ipynb               # 다중 태스크 BERT
│   ├── multitask_model_longformer.ipynb    # Longformer 확장
│   └── 통합 편향성 지수.ipynb                # 편향성 지수 분석
├── summarization/                          # 요약 및 추천 시스템
│   └── 1. sbert_based_generative.ipynb     # SBERT 기반 추천
├── data/                                   # 원본 및 전처리된 데이터
├── requirements.txt                        # 프로젝트 의존성
└── README.md                               # 프로젝트 문서
```

---

## 🚀 사용 방법

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 크롤링 의존성 설치
cd crawling
pip install -r requirements.txt
```

### 2. 데이터 수집
```bash
# 네이버 뉴스 크롤링 실행
cd crawling
python run_crawler.py
```

### 3. 모델 학습
```bash
# Jupyter 노트북 실행
jupyter notebook

# 순서대로 실행:
# 1. preprocess/news_preprocessing.ipynb
# 2. model/baseline_model.ipynb
# 3. model/multitask_model.ipynb
# 4. summarization/1. sbert_based_generative.ipynb
```

### 4. 뉴스 추천 시스템 사용
1. `summarization/1. sbert_based_generative.ipynb` 실행
2. 관심 키워드 입력 (예: "이재명 대장동")
3. 중립성 기반 추천 기사 확인

---

## 📊 주요 결과

### 베이스라인 모델 성능
- **F1-score**: 0.6406
- **정확도**: 0.6439
- **데이터**: 1,025개 레이블링된 기사

### 다중 태스크 모델 특징
- **정당 분류**: 3클래스 (국민의힘/민주당/그외)
- **감성 분석**: 3클래스 (긍정/중립/부정)
- **모델 아키텍처**: BERT + BiLSTM + 분류기
- **F1-score**: 0.9107

### 뉴스 추천 시스템
- **키워드 기반 필터링**: 사용자 관심 키워드로 관련 기사 추출
- **클러스터링**: 유사 기사 그룹화로 중복 제거
- **중립성 점수**: 편향성을 고려한 기사 순위화