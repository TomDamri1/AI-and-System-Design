# Voice Agents and Telephony

A voice agent is a text agent wrapped in a **hard real-time audio loop**. The
model work is familiar; what is new is that every stage runs against a
sub-second deadline and the user hears every millisecond of it. This page
covers the two architectures, the latency budget, turn-taking vocabulary, and
the phone-network plumbing.

## The two architectures

- **Chained: STT → LLM → TTS.** Speech recognition produces text, your existing
  text agent runs on it, speech synthesis reads the answer back. You get a
  **transcript at every boundary**, so debugging, evals and logging are the
  same problem you already solved. You pick each model independently and reuse
  the text agent, prompts and tools unchanged.
- **Speech-to-speech (realtime).** One model consumes audio and emits audio.
  Lower latency (no serial hand-offs), and it preserves **prosody** — tone,
  emphasis, hesitation, laughter — plus far more natural interruption handling.
  The cost is observability and control: there is no clean text seam to
  inspect, gate or replay.
- **Choosing:** chained for **predictable workflows and heavy tool use** —
  support triage, form-filling, anything auditable. Speech-to-speech for **open
  natural conversation** where feel beats controllability. Hybrids exist (a
  realtime model that hands structured tasks to a text agent).

## The latency budget

This is the defining constraint of the whole discipline.

- Human conversational turn gaps cluster around **200 ms**. You will not hit
  that, but it sets the reference.
- Defensible targets, **voice-to-voice** (caller stops talking → caller hears
  audio): **~500 ms feels natural, ~800 ms is the edge of tolerable, over 1 s
  reads as broken or as a dead line.** Treat any vendor's sub-300 ms claim as
  marketing measured on one stage in a lab.
- **Endpointing plus recognition alone can eat 350 ms** before the model has
  seen a single token. Add inference, first-token time, and synthesis, and a
  serial pipeline is over budget before it starts.
- The consequence: **stages must overlap and stream in parallel.** Recognize
  while the caller is still speaking, begin generating on partial input,
  synthesize from the first tokens, play audio as it is produced. Serial
  execution blows the budget every time.
- Tool calls are the usual budget killer. Speak a filler ("let me check that")
  or stream a partial answer while the call is in flight. See [[cost-latency]].

## Turn detection and endpointing

- **VAD** (voice activity detection): is there speech or silence in this audio
  frame. Cheap, acoustic, no understanding.
- **Endpointing**: the decision that the caller has *finished their turn*.
- **EOU** (end of utterance): the moment endpointing fires and generation
  starts.
- **Silence-threshold endpointing** is the naive version — wait N ms of
  silence. It is wrong on anyone who pauses mid-thought, reads a number off a
  card, or thinks out loud. **Semantic turn-detection models**, which judge
  whether the utterance sounds *complete* from meaning plus acoustics on top of
  VAD, are now the common default.
- The tuning trade-off is genuine and has no right answer: **short thresholds
  interrupt people, long ones feel sluggish.** Some stacks adapt the delay from
  observed pause statistics during the call.

## Barge-in

- The caller talks over the agent. The agent must **stop speaking immediately
  and discard queued audio** — including audio already buffered downstream.
- Distinguish a real interruption from **backchanneling** — "mm-hmm", "right",
  "okay" — which signals listening and must *not* stop playback. Naive VAD
  treats both identically and produces an agent that flinches constantly.
- **There is no undo on emitted audio.** Once a sentence is played, the caller
  heard it. Truncate the model's context to what was actually spoken, or the
  agent will reference things the caller never received.

## Telephony basics

- **SIP** is the *signalling* protocol: it sets up, negotiates and tears down
  calls. **Media flows separately** from signalling — a working SIP handshake
  says nothing about whether audio is arriving.
- **Trunks** are the configured connection to a carrier: **inbound** trunks
  receive calls, **outbound** trunks place them. A **dispatch rule** maps an
  incoming call to a session/agent.
- **Carriers and CPaaS providers** sit between the **PSTN** (the ordinary phone
  network) and your infrastructure; you rent numbers and trunks from them
  rather than touching the phone network directly.
- Real deployments need **DTMF** (keypad tones — IVR menus, entering account
  numbers) and **call transfer** to a human or another queue. Plan for both
  early; retrofitting transfer is painful.

## Transports

- **WebRTC** for browser and mobile clients: handles jitter, packet loss and
  echo cancellation for you. Do not rebuild this over raw sockets.
- **WebSocket** when your own server already holds the audio stream.
- **SIP** for the phone network.
- The common production shape puts **your agent server in the middle** rather
  than pointing a client straight at a model vendor, so it can mediate tool
  calls, redact PII and write the audit log.

## Why voice is harsher than chat

Underestimating this is the standard mistake.

- In chat, streaming tokens and the user's own reading speed hide two seconds
  of latency. In voice, **silence is the UI**: a 900 ms gap reads as a dropped
  call, and the caller starts saying "hello?".
- Failure modes chat does not have: **false endpointing** cuts the caller off
  mid-sentence; **missed endpointing** makes the agent talk over them;
  **recognition errors corrupt input silently** — accents, proper nouns, noise,
  code-switching — with no visible garbled text to signal the problem.
- **No scrollback.** The caller cannot re-read anything. Numbers, addresses,
  spelling and any commitment need **explicit read-back and confirmation**
  ("that's four-one-five... correct?"), and answers must be short enough to
  hold in working memory.

## Operational notes

- **Transcripts are the eval substrate for voice.** Log them per turn with
  timestamps, and measure endpointing errors and voice-to-voice latency
  percentiles as first-class metrics ([[evals-observability]]).
- Recording and transcription carry **consent obligations that vary by
  jurisdiction** (one-party vs all-party), plus retention and residency rules.
  Get this decided before launch, not after ([[enterprise-multitenancy]]).

## The hard part

**Every dial trades naturalness against correctness, and they are coupled.**
Faster endpointing cuts latency and cuts callers off. Speech-to-speech feels
human and removes the text seam your guardrails and evals were built on
([[guardrails]]). Aggressive barge-in makes the agent responsive and makes it
flinch at every "uh-huh". And unlike chat, **there is no undo** — a mistimed
interruption or a wrong number spoken aloud is already in the caller's ear.
Tune against recorded real calls, not your own voice in a quiet room.

## Related

- [[cost-latency]], [[evals-observability]], [[guardrails]],
  [[enterprise-multitenancy]], [[agent-loop]], [[tool-calling]],
  [[non-determinism]], [[antipatterns]]

Source: docs.livekit.io/agents/build/turns (VAD, endpointing delays, semantic
turn-detector model, interruptions vs backchanneling); docs.livekit.io/sip (SIP
trunks, dispatch rules); developers.openai.com/api/docs/guides/voice-agents
(chained vs speech-to-speech trade-offs). Latency figures are engineering
consensus ranges, not vendor benchmarks — measure your own voice-to-voice p95.
