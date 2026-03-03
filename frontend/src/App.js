import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5001';

/* ============================================================
   SOUND EFFECTS
   ============================================================ */
const SoundContext = React.createContext({ play: () => {}, muted: true });

function useSounds() {
  return React.useContext(SoundContext);
}

function SoundProvider({ children }) {
  const [muted, setMuted] = useState(() => {
    const saved = localStorage.getItem('soundMuted');
    return saved === null ? false : saved === 'true';
  });
  const audioContextRef = useRef(null);

  const getContext = () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioContextRef.current;
  };

  const play = useCallback((type) => {
    if (muted) return;
    try {
      const ctx = getContext();

      switch (type) {
        case 'click': {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.frequency.value = 600;
          osc.type = 'sine';
          gain.gain.setValueAtTime(0.1, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
          osc.start(ctx.currentTime);
          osc.stop(ctx.currentTime + 0.1);
          break;
        }
        case 'page': {
          // Page flip sound - quick snap with frequency sweep
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const filter = ctx.createBiquadFilter();

          osc.connect(filter);
          filter.connect(gain);
          gain.connect(ctx.destination);

          // Start high, sweep down quickly (like paper flicking)
          osc.frequency.setValueAtTime(1200, ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(150, ctx.currentTime + 0.08);
          osc.type = 'square';

          // Bandpass filter for papery quality
          filter.type = 'bandpass';
          filter.frequency.value = 800;
          filter.Q.value = 1;

          // Quick attack, quick decay
          gain.gain.setValueAtTime(0.08, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);

          osc.start(ctx.currentTime);
          osc.stop(ctx.currentTime + 0.1);
          break;
        }
        case 'complete': {
          // Play a little melody
          const notes = [523, 659, 784]; // C5, E5, G5
          notes.forEach((freq, i) => {
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.connect(g);
            g.connect(ctx.destination);
            o.frequency.value = freq;
            o.type = 'sine';
            g.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.15);
            g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.15 + 0.3);
            o.start(ctx.currentTime + i * 0.15);
            o.stop(ctx.currentTime + i * 0.15 + 0.3);
          });
          break;
        }
        default:
          break;
      }
    } catch (e) {
      // Audio not supported
    }
  }, [muted]);

  const toggleMute = () => {
    setMuted(prev => {
      localStorage.setItem('soundMuted', String(!prev));
      return !prev;
    });
  };

  return (
    <SoundContext.Provider value={{ play, muted, toggleMute }}>
      {children}
    </SoundContext.Provider>
  );
}

function SoundToggle() {
  const { muted, toggleMute } = useSounds();

  return (
    <button
      className="sound-toggle"
      onClick={toggleMute}
      aria-label={muted ? 'Unmute sounds' : 'Mute sounds'}
    >
      <span className="sound-icon">{muted ? '🔇' : '🔊'}</span>
    </button>
  );
}

/* ============================================================
   THEME TOGGLE
   ============================================================ */
function ThemeToggle() {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved;
    // Defensive check for test environments
    try {
      const mq = window.matchMedia?.('(prefers-color-scheme: dark)');
      return mq?.matches ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <button
      className="theme-toggle"
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <span className={`theme-icon ${theme === 'light' ? 'sun' : 'moon'}`}>
        {theme === 'light' ? '☀️' : '🌙'}
      </span>
    </button>
  );
}

/* ============================================================
   ANIMATED TITLE HELPER
   ============================================================ */
function AnimatedTitle({ text, delay = 0 }) {
  return text.split('').map((char, i) => (
    <span
      key={i}
      className="title-char"
      style={{ animationDelay: `${delay + i * 0.05}s` }}
    >
      {char}
    </span>
  ));
}

/* ============================================================
   LANDING PAGE
   ============================================================ */
function LandingPage({ onStart }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`landing ${visible ? 'visible' : ''}`}>
      <div className="landing-content">
        <div className="landing-logo">
          <span className="logo-icon" role="img" aria-label="open book">📖</span>
        </div>
        <h1 className="landing-title">
          <span className="title-equal"><AnimatedTitle text="Equal" delay={0.3} /></span>
          <span className="title-tales"><AnimatedTitle text="Tales" delay={0.55} /></span>
        </h1>
        <p className="landing-subtitle">
          AI-powered stories that change what children believe is possible
        </p>
        <p className="landing-description">
          Type the stereotype your child has expressed. We'll create a personalized,
          illustrated story featuring a real woman who proved it wrong.
        </p>
        <div className="social-proof-badge">
          <span className="badge-icon">✨</span>
          <span>Featuring <strong>50+</strong> inspiring women who broke barriers</span>
        </div>
        <button className="btn-primary btn-cta" onClick={onStart}>
          Try It Now
        </button>
        <div className="landing-stats">
          <div className="stat">
            <span className="stat-number">Age 3</span>
            <span className="stat-label">When children absorb stereotypes</span>
          </div>
          <div className="stat">
            <span className="stat-number">Age 6</span>
            <span className="stat-label">When girls believe boys are "smarter"</span>
          </div>
          <div className="stat">
            <span className="stat-number">5 pages</span>
            <span className="stat-label">Personalized illustrated story</span>
          </div>
        </div>
        <p className="landing-footnote">
          Powered by Goose + Claude — Built for CreateHER Fest #75HER Challenge
        </p>
      </div>
    </div>
  );
}

/* ============================================================
   INPUT FORM
   ============================================================ */
const FALLBACK_EXAMPLES = [
  { text: "Girls can't do math", emoji: "🔢" },
  { text: "Science is for boys", emoji: "🔬" },
  { text: "Girls aren't strong enough", emoji: "💪" },
  { text: "Boys are better at sports", emoji: "⚽" },
  { text: "Girls should be quiet and polite", emoji: "🤫" },
  { text: "Girls can't be leaders", emoji: "👑" },
  { text: "Technology is for boys", emoji: "💻" },
  { text: "Girls can't build things", emoji: "🏗️" },
  { text: "Being a mom means giving up your dreams", emoji: "👩‍👧" },
  { text: "It's too late to start something new", emoji: "⏰" },
];

function InputForm({ onGenerate, onBack }) {
  const [stereotype, setStereotype] = useState('');
  const [childName, setChildName] = useState('');
  const [childAge, setChildAge] = useState(6);
  const [examples, setExamples] = useState(FALLBACK_EXAMPLES);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/api/examples`)
      .then(r => {
        if (!r.ok) throw new Error('Failed to fetch');
        return r.json();
      })
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setExamples(data);
        }
      })
      .catch(() => {
        // Keep the fallback examples that were set as initial state
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!stereotype.trim()) return;
    onGenerate({
      stereotype: stereotype.trim(),
      child_name: childName.trim() || 'Lily',
      child_age: childAge
    });
  };

  return (
    <div className={`input-form-container ${visible ? 'visible' : ''}`}>
      <button className="back-btn" onClick={onBack}>
        ← Back
      </button>
      <div className="input-form-header">
        <h2>What stereotype do you want to counter?</h2>
        <p>Type what your child said or believes, or pick an example below.</p>
      </div>

      <div className="examples-grid">
        {examples.map((ex, i) => (
          <button
            key={i}
            className={`example-btn ${stereotype === ex.text ? 'active' : ''}`}
            onClick={() => setStereotype(ex.text)}
          >
            <span className="example-emoji">{ex.emoji}</span>
            <span className="example-text">{ex.text}</span>
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="story-form">
        <div className="form-group">
          <label htmlFor="stereotype">Or type your own:</label>
          <textarea
            id="stereotype"
            value={stereotype}
            onChange={(e) => setStereotype(e.target.value.slice(0, 500))}
            placeholder='e.g., "My daughter thinks only boys can be engineers"'
            rows={3}
            maxLength={500}
          />
          <div className="char-counter">
            <span className={stereotype.length > 450 ? 'warning' : ''}>
              {stereotype.length}/500
            </span>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="childName">Child's name:</label>
            <input
              id="childName"
              type="text"
              value={childName}
              onChange={(e) => setChildName(e.target.value)}
              placeholder="Lily"
            />
          </div>
          <div className="form-group">
            <label htmlFor="childAge">Child's age: <strong>{childAge}</strong></label>
            <input
              id="childAge"
              type="range"
              min={3}
              max={10}
              value={childAge}
              onChange={(e) => setChildAge(parseInt(e.target.value))}
            />
            <div className="age-labels">
              <span>3</span>
              <span>10</span>
            </div>
          </div>
        </div>

        <button type="submit" className="btn-primary btn-generate" disabled={!stereotype.trim()}>
          Create My Story
        </button>
      </form>
    </div>
  );
}

/* ============================================================
   GENERATION PROGRESS
   ============================================================ */
const WAIT_TIPS = [
  "Did you know? Stories help children develop empathy and emotional intelligence.",
  "Research shows representation in stories shapes children's aspirations.",
  "Reading together strengthens the parent-child bond.",
  "Children who see diverse role models dream bigger dreams.",
  "A single story can change how a child sees their potential.",
  "The best time to counter stereotypes is before age 7.",
  "Girls who read about female scientists are more likely to pursue STEM.",
  "Children remember stories 22 times more than facts alone.",
  "Diverse books help all children develop cultural awareness.",
  "Kids ask 'why' about 300 times a day — stories help answer those questions.",
  "Picture books activate the same brain regions as real experiences.",
  "Children form gender stereotypes as early as age 2.",
  "Reading fiction increases a child's ability to understand others' perspectives.",
  "Stories featuring real role models have lasting impact on career aspirations.",
  "The women in our stories broke barriers so today's girls can dream without limits.",
];

function GenerationProgress({ status, storyData, illustrations, qaResult, realWoman, elapsedTime }) {
  const [tipIndex, setTipIndex] = useState(0);
  const [tipVisible, setTipVisible] = useState(true);

  useEffect(() => {
    if (elapsedTime < 10) return; // Don't show tips until 10s in
    const interval = setInterval(() => {
      setTipVisible(false);
      setTimeout(() => {
        setTipIndex(prev => (prev + 1) % WAIT_TIPS.length);
        setTipVisible(true);
      }, 300);
    }, 8000);
    return () => clearInterval(interval);
  }, [elapsedTime]);

  const steps = [
    { key: 'classify', label: 'Understanding the stereotype', icon: '🔍' },
    { key: 'woman', label: 'Finding an inspiring woman', icon: '✨' },
    { key: 'story', label: 'Writing the story', icon: '📝' },
    { key: 'qa', label: 'Quality check', icon: '✅' },
    { key: 'illustrate', label: 'Painting illustrations', icon: '🎨' },
  ];

  const getStepStatus = (stepKey) => {
    switch (stepKey) {
      case 'classify': return status === 'classifying' ? 'active' : (realWoman || storyData ? 'done' : 'pending');
      case 'woman': return status === 'selecting_woman' ? 'active' : (realWoman ? 'done' : 'pending');
      case 'story': return status === 'generating_story' ? 'active' : (storyData ? 'done' : 'pending');
      case 'qa': return status === 'qa_check' ? 'active' : (qaResult ? 'done' : 'pending');
      case 'illustrate': return status === 'illustrating' ? 'active' : (illustrations.filter(Boolean).length === 5 ? 'done' : illustrations.some(Boolean) ? 'active' : 'pending');
      default: return 'pending';
    }
  };

  const illustrationCount = illustrations.filter(Boolean).length;
  const completedSteps = steps.filter(s => getStepStatus(s.key) === 'done').length;
  const progressPercent = Math.min(100, (completedSteps / steps.length) * 100 + (status === 'illustrating' ? (illustrationCount / 5) * 20 : 0));

  return (
    <div className="generation-progress">
      <div className="progress-header">
        <h2>Creating your story...</h2>
        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${progressPercent}%` }} />
        </div>
        {elapsedTime > 0 && (
          <p className="elapsed-time">{Math.round(elapsedTime)}s elapsed</p>
        )}
      </div>

      <div className="progress-steps">
        {steps.map((step) => {
          const s = getStepStatus(step.key);
          return (
            <div key={step.key} className={`progress-step ${s}`}>
              <span className="step-icon">
                {s === 'done' ? '✓' : s === 'active' ? step.icon : '○'}
              </span>
              <span className="step-label">
                {step.label}
                {step.key === 'illustrate' && illustrationCount > 0 && ` (${illustrationCount}/5)`}
              </span>
            </div>
          );
        })}
      </div>

      {realWoman && (
        <div className="woman-reveal">
          <span className="woman-reveal-label">Featuring</span>
          <strong>{realWoman.name}</strong>
          <span className="woman-reveal-achievement">{realWoman.achievement}</span>
        </div>
      )}

      {elapsedTime >= 10 && (
        <div className={`wait-tip ${tipVisible ? 'visible' : ''}`}>
          <span className="tip-icon">💡</span>
          <p>{WAIT_TIPS[tipIndex]}</p>
        </div>
      )}
    </div>
  );
}

/* ============================================================
   TYPEWRITER TEXT COMPONENT
   ============================================================ */
function TypewriterText({ text, speed = 20, onComplete }) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const onCompleteRef = useRef(onComplete);
  const timeoutRef = useRef(null);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    setDisplayedText('');
    setIsComplete(false);
    let i = 0;

    const getDelay = (char) => {
      if (['.', '!', '?'].includes(char)) return speed * 8;
      if ([',', ';', ':'].includes(char)) return speed * 4;
      if (char === '—' || char === '–') return speed * 6;
      return speed;
    };

    const typeNext = () => {
      if (i < text.length) {
        setDisplayedText(text.slice(0, i + 1));
        const delay = getDelay(text[i]);
        i++;
        timeoutRef.current = setTimeout(typeNext, delay);
      } else {
        setIsComplete(true);
        if (onCompleteRef.current) onCompleteRef.current();
      }
    };

    timeoutRef.current = setTimeout(typeNext, speed);
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [text, speed]);

  return (
    <span className={isComplete ? 'typewriter-complete' : 'typewriter-typing'}>
      {displayedText}
      {!isComplete && <span className="typewriter-cursor">|</span>}
    </span>
  );
}

/* ============================================================
   STORYBOOK VIEWER
   ============================================================ */
function StorybookViewer({ storyData, illustrations, qaResult, realWoman, onReset }) {
  const [currentPage, setCurrentPage] = useState(0);
  const [showCompanion, setShowCompanion] = useState(false);
  const [pageTransition, setPageTransition] = useState('');
  const [showTypewriter, setShowTypewriter] = useState(true);
  const [seenPages, setSeenPages] = useState(new Set([0]));
  const [swipeOffset, setSwipeOffset] = useState(0);
  const touchStartRef = useRef(null);
  const { play } = useSounds();

  const pages = storyData?.pages || [];
  const totalPages = pages.length;

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        goNext();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        goPrev();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  });

  // Touch/swipe handlers
  const handleTouchStart = (e) => {
    touchStartRef.current = e.touches[0].clientX;
  };

  const handleTouchMove = (e) => {
    if (!touchStartRef.current) return;
    const diff = e.touches[0].clientX - touchStartRef.current;
    // Limit swipe feedback to ±60px
    setSwipeOffset(Math.max(-60, Math.min(60, diff * 0.3)));
  };

  const handleTouchEnd = (e) => {
    if (!touchStartRef.current) return;
    const diff = e.changedTouches[0].clientX - touchStartRef.current;
    setSwipeOffset(0);

    // Threshold of 50px for swipe
    if (diff > 50) {
      goPrev();
    } else if (diff < -50) {
      goNext();
    }
    touchStartRef.current = null;
  };

  const navigateToPage = (newPage, direction) => {
    setPageTransition(`exit-${direction}`);
    setTimeout(() => {
      setCurrentPage(newPage);
      // Show typewriter for pages not yet seen (check BEFORE updating seenPages)
      const isNewPage = !seenPages.has(newPage);
      if (isNewPage) {
        setShowTypewriter(true);
      }
      // Don't add to seenPages here - do it when typewriter completes
      setPageTransition(`enter-${direction}`);
      setTimeout(() => setPageTransition(''), 500);
    }, 200);
  };

  const goNext = () => {
    if (showCompanion) return;
    if (currentPage < totalPages - 1) {
      navigateToPage(currentPage + 1, 'left');
    } else {
      play('complete');
      setShowCompanion(true);
    }
  };

  const goPrev = () => {
    if (showCompanion) {
      setShowCompanion(false);
    } else if (currentPage > 0) {
      navigateToPage(currentPage - 1, 'right');
    }
  };

  if (showCompanion) {
    return (
      <div className="storybook">
        <div className="companion-section">
          <h2>After the Story</h2>

          {realWoman && (
            <div className="companion-card woman-card">
              <h3>About {realWoman.name}</h3>
              <p className="woman-era">{realWoman.era}</p>
              <p>{storyData.real_woman_achievement || realWoman.achievement}</p>
            </div>
          )}

          {storyData.discussion_prompts && storyData.discussion_prompts.length > 0 && (
            <div className="companion-card">
              <h3>Talk About It</h3>
              <ul className="discussion-prompts">
                {storyData.discussion_prompts.map((prompt, i) => (
                  <li key={i}>{prompt}</li>
                ))}
              </ul>
            </div>
          )}

          {storyData.activity_suggestion && (
            <div className="companion-card">
              <h3>Try This Activity</h3>
              <p>{storyData.activity_suggestion}</p>
            </div>
          )}

          {qaResult && (
            <div className="qa-badge">
              <span className="qa-icon">{qaResult.passed ? '✅' : '⚠️'}</span>
              <span className="qa-text">
                Story verified: {qaResult.passed ? 'No stereotype reinforcement detected' : 'Review suggested'}
              </span>
              <span className="qa-score">Quality score: {qaResult.score}/10</span>
            </div>
          )}

          <div className="companion-nav">
            <button className="btn-secondary" onClick={goPrev}>← Back to Story</button>
            <button className="btn-primary" onClick={onReset}>Create Another Story</button>
          </div>
        </div>
      </div>
    );
  }

  const page = pages[currentPage];
  const illustration = illustrations[currentPage];
  const isFirstView = showTypewriter;

  return (
    <div className="storybook">
      <div className="storybook-header">
        <button className="exit-btn" onClick={onReset} aria-label="Exit story">
          ✕
        </button>
        <h1 className="story-title">{storyData.title}</h1>
        <div className="page-indicator">
          {pages.map((_, i) => (
            <button
              key={i}
              className={`page-dot ${i === currentPage ? 'active' : ''} ${seenPages.has(i) ? 'seen' : ''}`}
              onClick={() => {
                if (i !== currentPage) navigateToPage(i, i > currentPage ? 'left' : 'right');
              }}
              aria-label={`Page ${i + 1}`}
            />
          ))}
        </div>
      </div>

      <div
        className={`storybook-page ${pageTransition}`}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        style={swipeOffset ? { transform: `translateX(${swipeOffset}px) rotateY(${swipeOffset * 0.05}deg)` } : {}}
      >
        <div className="page-illustration">
          {illustration ? (
            <img
              src={illustration}
              alt={page?.illustration_description || `Illustration for page ${currentPage + 1}`}
              className="illustration-img"
              onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling && (e.target.nextSibling.style.display = 'flex'); }}
            />
          ) : null}
          <div className="illustration-placeholder" style={illustration ? {display: 'none'} : {}}>
            <span>🎨</span>
            <p>{illustration ? 'Image unavailable' : 'Illustration loading...'}</p>
          </div>
        </div>

        <div className="page-content">
          <div className="page-label">{page?.page_title}</div>
          <div className="page-text">
            {isFirstView ? (
              <TypewriterText
                text={page?.text || ''}
                speed={25}
                onComplete={() => {
                  setShowTypewriter(false);
                  setSeenPages(prev => new Set([...prev, currentPage]));
                }}
              />
            ) : (
              page?.text
            )}
          </div>
          <div className="page-number">— {currentPage + 1} of {totalPages} —</div>
        </div>
      </div>

      <div className="storybook-nav">
        <button
          className="nav-btn nav-prev"
          onClick={goPrev}
          disabled={currentPage === 0}
        >
          ← Previous
        </button>
        <button className="nav-btn nav-next" onClick={goNext}>
          {currentPage === totalPages - 1 ? 'Discussion & Activities →' : 'Next →'}
        </button>
      </div>

      <p className="nav-hint">Use arrow keys or swipe to navigate</p>
    </div>
  );
}

/* ============================================================
   MAIN APP
   ============================================================ */
function App() {
  const [screen, setScreen] = useState('landing');
  const [storyData, setStoryData] = useState(null);
  const [illustrations, setIllustrations] = useState([]);
  const [classification, setClassification] = useState(null);
  const [realWoman, setRealWoman] = useState(null);
  const [lastInputs, setLastInputs] = useState(null);
  const [qaResult, setQaResult] = useState(null);
  const [genStatus, setGenStatus] = useState('');
  const [error, setError] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const timerRef = useRef(null);

  const startTimer = () => {
    const startTime = Date.now();
    timerRef.current = setInterval(() => {
      setElapsedTime((Date.now() - startTime) / 1000);
    }, 500);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const handleGenerate = useCallback((inputs) => {
    setLastInputs(inputs);
    setScreen('generating');
    setStoryData(null);
    setIllustrations([null, null, null, null, null]);
    setClassification(null);
    setRealWoman(null);
    setQaResult(null);
    setError(null);
    setGenStatus('classifying');
    setElapsedTime(0);
    startTimer();

    fetch(`${API_BASE}/api/generate/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputs)
    }).then(response => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      function processStream() {
        reader.read().then(({ done, value }) => {
          if (done) {
            stopTimer();
            // If stream ended but we have story data, show it anyway
            setScreen(prev => prev === 'generating' ? (storyData ? 'storybook' : prev) : prev);
            return;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop();

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const event = JSON.parse(line.slice(6));

                switch (event.type) {
                  case 'status':
                    if (event.message.includes('Understanding')) setGenStatus('classifying');
                    else if (event.message.includes('Finding')) setGenStatus('selecting_woman');
                    else if (event.message.includes('Writing')) setGenStatus('generating_story');
                    else if (event.message.includes('Checking') || event.message.includes('Quality')) setGenStatus('qa_check');
                    else if (event.message.includes('Painting') || event.message.includes('illustration')) setGenStatus('illustrating');
                    break;
                  case 'classification':
                    setClassification(event.data);
                    break;
                  case 'real_woman':
                    setRealWoman(event.data);
                    break;
                  case 'story':
                    setStoryData(event.data);
                    break;
                  case 'qa_result':
                    setQaResult(event.data);
                    break;
                  case 'illustration':
                    setIllustrations(prev => {
                      const updated = [...prev];
                      updated[event.page] = event.url;
                      return updated;
                    });
                    break;
                  case 'complete':
                    stopTimer();
                    setScreen('storybook');
                    break;
                  case 'error':
                    stopTimer();
                    setError(event.message);
                    break;
                  default:
                    break;
                }
              } catch (e) {
                // Skip unparseable lines
              }
            }
          }

          processStream();
        });
      }

      processStream();
    }).catch(err => {
      stopTimer();
      setError(`Connection error: ${err.message}. Make sure the backend is running.`);
    });
  }, []);

  const handleReset = () => {
    setScreen('input');
    setStoryData(null);
    setIllustrations([]);
    setClassification(null);
    setRealWoman(null);
    setQaResult(null);
    setGenStatus('');
    setError(null);
    setElapsedTime(0);
  };

  return (
    <SoundProvider>
    <div className="app">
      <div className="app-controls">
        <SoundToggle />
        <ThemeToggle />
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <div className="error-actions">
            {lastInputs && <button onClick={() => handleGenerate(lastInputs)}>Try Again</button>}
            <button onClick={() => { setError(null); setScreen('input'); }}>Change Input</button>
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        </div>
      )}

      {screen === 'landing' && (
        <LandingPage onStart={() => setScreen('input')} />
      )}

      {screen === 'input' && (
        <InputForm onGenerate={handleGenerate} onBack={() => setScreen('landing')} />
      )}

      {screen === 'generating' && (
        <GenerationProgress
          status={genStatus}
          storyData={storyData}
          illustrations={illustrations}
          qaResult={qaResult}
          realWoman={realWoman}
          elapsedTime={elapsedTime}
        />
      )}

      {screen === 'storybook' && storyData && (
        <StorybookViewer
          storyData={storyData}
          illustrations={illustrations}
          qaResult={qaResult}
          realWoman={realWoman}
          onReset={handleReset}
        />
      )}
    </div>
    </SoundProvider>
  );
}

export default App;
