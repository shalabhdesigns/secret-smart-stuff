# R2 — LLM humour, LLM-as-judge, writers' rooms (verified 27 Oct 2026)

Labels: [F] research finding · [E] expert/practitioner · [H] hypothesis.

LLM humour quality and sameness
- 1,008 ChatGPT jokes: >90% were the same 25 jokes. [F] Jentzsch & Kersting 2023: https://arxiv.org/abs/2306.04563v1
- 20 professional comedians found LLM output "bland, biased comedy tropes". [F, qualitative] Mirowski et al. 2024:
  https://arxiv.org/abs/2405.20956
- Models trail humans on New Yorker caption tasks; humans prefer human explanations >2/3 of the time. [F] Hessel et al.,
  ACL 2023: https://aclanthology.org/2023.acl-long.41/
- GPT-4/Claude captions underperform top humans and are more verbose. [F] Zhang et al. 2024: https://arxiv.org/abs/2406.10522
- LLMs are good at REMOVING humour ("unfunning"). [F] Horvitz et al., ACL 2024: https://aclanthology.org/2024.acl-short.76
- LLM outputs are more similar to each other than humans are to each other — switching model doesn't fix sameness. [F]
  Wenger & Kenett 2025: https://arxiv.org/abs/2501.19361v1
- AI ideas raise individual novelty but make stories 10.7% more similar to each other. [F] Doshi & Hauser 2024 (Science
  Advances), via https://news.exeter.ac.uk/?p=13749
- LLM stories fall short on novelty/surprise/diversity per experts — but LLM and non-expert raters rate them MORE creative. [F]
  Ismayilzada et al. 2024: https://arxiv.org/abs/2411.02316

What helped (modestly)
- Association-first generation + humour policy cut "already known" jokes 27%→18%; funniness gain not significant. [F]
  Tikhonov & Shtykovskiy, ICCC 2024: https://arxiv.org/abs/2405.07280
- Plan-search over varied humour strategies + novelty filtering + judge-driven revision: +15.4% humour score (13 judges,
  preprint). [F, weak] https://arxiv.org/abs/2508.11429
- Multi-hop "thought leaps" + external knowledge help. [F/H] https://arxiv.org/abs/2410.10370v2

LLM-as-judge
- Position, verbosity and self-enhancement biases; ~80% agreement with humans on general chat. [F] Zheng et al., NeurIPS 2023:
  https://arxiv.org/abs/2306.05685
- Swapping answer order flipped 66/80 verdicts; fix = evidence before score + average both orders + humans on hard cases. [F]
  Wang et al. 2023: https://arxiv.org/abs/2305.17926v2
- Models recognise and favour their own generations. [F] Panickssery et al., NeurIPS 2024: https://arxiv.org/abs/2404.13076v1
- A jury of smaller models from different families beats one big judge, less biased, 7× cheaper. [F] Verga et al. 2024:
  https://arxiv.org/abs/2404.18796v2
- Pairwise preferences flip ~35% under distractor features vs 9% for absolute scores. [F] Tripathi et al. 2025:
  https://arxiv.org/abs/2504.14716
- GPT-4 picks the funnier caption 66.5–77.5% vs an expert's 94.3% (easy top-vs-mid task). [F] Zhang et al. 2024 (Table 2).
- 9,894 Cards-Against rounds: models agree with humans only modestly and with each other much more. [F]
  Fettach et al. 2026: https://arxiv.org/abs/2604.08757

Writers' rooms [E]
- Room "breaks" story, one writer drafts, room rewrites to a table draft, table read, more rewrites; energy leaving the room
  = the joke failed. Michael Jamin: https://michaeljamin.substack.com/p/whats-the-rewrite-process-like-in
- "Write it out first with no jokes" — story and wants first. Megan Ganz, Chortle 2022:
  https://www.chortle.co.uk/features/2022/05/13/50783/want_to_write_a_sitcom
- Joke "alts" files; punch-up after table reads. https://scriptation.com/blog/how-to-write-joke-alts-tv-and-film/ (weak source)
- Pixar Braintrust: candour; "early on, all of our movies suck". Ed Catmull, Fast Company 2014:
  https://www.fastcompany.com/3027135/inside-the-pixar-braintrust
- Paula Finn interviews (pitching to the showrunner's taste, "savers"): https://screenwritingmagazine.com/?p=4500

Decisions taken (docs/TEMPLATE.md): story-first then jokes; association/observation-first ideation at high temperature
with cliché + repetition filters; judge = different model, blind, both orders, evidence before score; anchored absolute
scores to screen, pairwise only between finalists; LLM judge is a coarse filter — the owner and real audience data are the
final selector, and the judge is calibrated against them (perf.py, lessons.py).
Limit: only Anthropic models are available to this pipeline, so a cross-family jury is not possible now (noted risk).
