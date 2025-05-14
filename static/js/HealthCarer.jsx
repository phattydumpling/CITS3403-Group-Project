import React, { useState } from "react";

// Simple confetti component (SVG-based, minimal)
const Confetti = () => (
  <svg
    className="confetti"
    width="100%"
    height="100%"
    style={{
      position: "absolute",
      top: 0,
      left: 0,
      pointerEvents: "none",
      zIndex: 2,
    }}
  >
    {[...Array(30)].map((_, i) => (
      <circle
        key={i}
        cx={Math.random() * 100 + "%"}
        cy={Math.random() * 100 + "%"}
        r={Math.random() * 4 + 2}
        fill={
          [
            "#A7C7E7", // pastel blue
            "#FFD6B0", // pastel orange
            "#B6E2A1", // pastel green
            "#FFB3B3", // pastel red
          ][Math.floor(Math.random() * 4)]
        }
        opacity="0.8"
      />
    ))}
  </svg>
);

const CATEGORIES = [
  {
    key: "emotional",
    label: "Emotional",
    color: "#A7C7E7",
    placeholder: "Meditate for 5 minutes",
  },
  {
    key: "physical",
    label: "Physical",
    color: "#FFD6B0",
    placeholder: "Enter your physical goal...",
  },
  {
    key: "study",
    label: "Study",
    color: "#B6E2A1",
    placeholder: "Enter your study goal...",
  },
];

const HealthCarer = () => {
  const [inputs, setInputs] = useState({
    emotional: "",
    physical: "",
    study: "",
  });
  const [goals, setGoals] = useState({
    emotional: null,
    physical: null,
    study: null,
  });
  const [animated, setAnimated] = useState({
    emotional: false,
    physical: false,
    study: false,
  });

  const allSelected =
    goals.emotional && goals.physical && goals.study;

  // For gradient background when all selected
  const gradientBg = allSelected
    ? {
        background: `linear-gradient(120deg, #A7C7E7, #FFD6B0, #B6E2A1)`,
        transition: "background 0.5s",
      }
    : {};

  const handleInputChange = (category, value) => {
    setInputs((prev) => ({
      ...prev,
      [category]: value,
    }));
  };

  const handleSubmit = (category) => {
    if (inputs[category].trim() === "") return;
    setGoals((prev) => ({
      ...prev,
      [category]: inputs[category].trim(),
    }));
    setAnimated((prev) => ({
      ...prev,
      [category]: false,
    }));
    // Trigger animation after a tick
    setTimeout(() => {
      setAnimated((prev) => ({
        ...prev,
        [category]: true,
      }));
    }, 10);
  };

  return (
    <div
      className={`health-carer-container${allSelected ? " all-selected" : ""}`}
      style={gradientBg}
    >
      <header className="health-carer-header">
        <h1>Daily Goals</h1>
        <p className="health-carer-subtitle">
          Set your goal for each area: <strong>Emotional</strong>,{" "}
          <strong>Physical</strong>, <strong>Study</strong>
        </p>
      </header>
      <div className="goal-columns">
        {CATEGORIES.map((cat) => (
          <div className="goal-column" key={cat.key}>
            <h2
              className="goal-category-title"
              style={{
                color: cat.color,
              }}
            >
              {cat.label}
            </h2>
            <div className="goal-input-area">
              {goals[cat.key] ? (
                <div
                  className={`goal-card user-goal-card fade-in-up${animated[cat.key] ? " show" : ""}`}
                  style={{
                    background: cat.color,
                    borderColor: cat.color,
                  }}
                >
                  <span className="goal-label">{goals[cat.key]}</span>
                </div>
              ) : (
                <form
                  className="goal-input-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSubmit(cat.key);
                  }}
                  autoComplete="off"
                >
                  <input
                    type="text"
                    className="goal-input"
                    placeholder={cat.placeholder}
                    value={inputs[cat.key]}
                    onChange={(e) => handleInputChange(cat.key, e.target.value)}
                    maxLength={60}
                  />
                  <button
                    type="submit"
                    className="goal-submit-btn"
                    style={{
                      background: cat.color,
                      borderColor: cat.color,
                    }}
                  >
                    Submit
                  </button>
                </form>
              )}
            </div>
          </div>
        ))}
      </div>
      {allSelected && (
        <>
          <Confetti />
          <div className="success-message">
            <span role="img" aria-label="tada">
              🎉
            </span>{" "}
            All goals set! You're ready to crush your day!
          </div>
        </>
      )}
    </div>
  );
};

export default HealthCarer;