import React, { useRef, useEffect, useState } from "react";

const WIDTH = 600;
const HEIGHT = 800;

const MODES = [
  {
    bg: "#1e1e1e",
    player: "#C8C832",
    item: "#32C8C8",
    giant: "#FF0000",
    obstacle: "#800080",
    text: "#ffffff"
  },
  {
    bg: "#ffffff",
    player: "#0064C8",
    item: "#32C8C8",
    giant: "#FF0000",
    obstacle: "#800080",
    text: "#000000"
  }
];

const Game1930 = () => {
  const canvasRef = useRef(null);
  const [paused, setPaused] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [score, setScore] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [modeIndex, setModeIndex] = useState(0);
  const [lastClap, setLastClap] = useState(0);
  const [lastTheme, setLastTheme] = useState(0);

  const player = useRef({ x: WIDTH / 2 - 25, y: HEIGHT - 60, width: 50, height: 50, speed: 5 });
  const items = useRef([]);
  const giants = useRef([]);
  const obstacles = useRef([]);
  const keys = useRef({});
  const timer = useRef(0);

  const currentTheme = MODES[modeIndex];

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const handleKeyDown = e => keys.current[e.key] = true;
    const handleKeyUp = e => keys.current[e.key] = false;

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("keyup", handleKeyUp);

    const loop = () => {
      if (!paused && !gameOver) {
        // Move player
        if (keys.current["ArrowLeft"]) player.current.x -= player.current.speed;
        if (keys.current["ArrowRight"]) player.current.x += player.current.speed;
        player.current.x = Math.max(0, Math.min(WIDTH - player.current.width, player.current.x));

        // Score logic
        if (score >= lastClap + 100) {
          console.log("👏 Clap Sound!");
          setLastClap(score);
        }

        if (score >= lastTheme + 150) {
          setModeIndex((prev) => (prev + 1) % MODES.length);
          setLastTheme(score);
        }

        // Spawn items
        timer.current++;
        if (timer.current > 30) {
          timer.current = 0;
          items.current.push({ x: Math.random() * (WIDTH - 20), y: 0, r: 10 });
          if (score > 0 && score % 5 === 0)
            giants.current.push({ x: Math.random() * (WIDTH - 30), y: 0, r: 15 });
          if (Math.random() < 0.1)
            obstacles.current.push({ x: Math.random() * (WIDTH - 30), y: 0, r: 20 });
        }

        // Move and check collision
        items.current = items.current.filter(item => {
          item.y += 4;
          if (checkCollision(item.x, item.y, item.r)) {
            setScore(s => s + 1);
            return false;
          }
          return item.y < HEIGHT;
        });

        giants.current = giants.current.filter(g => {
          g.y += 3;
          if (checkCollision(g.x, g.y, g.r)) {
            setScore(s => s + 10);
            return false;
          }
          return g.y < HEIGHT;
        });

        obstacles.current = obstacles.current.filter(o => {
          o.y += 5;
          if (checkCollision(o.x, o.y, o.r)) {
            console.log("😱 Oh no!");
            setGameOver(true);
            return false;
          }
          return o.y < HEIGHT;
        });

        setHighScore(h => Math.max(h, score));
      }

      draw(ctx);
      requestAnimationFrame(loop);
    };

    loop();

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("keyup", handleKeyUp);
    };
  }, [paused, gameOver, score, modeIndex]);

  const checkCollision = (x, y, r) => {
    return (
      x > player.current.x &&
      x < player.current.x + player.current.width &&
      y > player.current.y &&
      y < player.current.y + player.current.height
    );
  };

  const draw = (ctx) => {
    ctx.fillStyle = currentTheme.bg;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    ctx.fillStyle = currentTheme.player;
    ctx.fillRect(player.current.x, player.current.y, player.current.width, player.current.height);

    items.current.forEach(item => drawCircle(ctx, item.x, item.y, item.r, currentTheme.item));
    giants.current.forEach(g => drawCircle(ctx, g.x, g.y, g.r, currentTheme.giant));
    obstacles.current.forEach(o => drawCircle(ctx, o.x, o.y, o.r, currentTheme.obstacle));

    ctx.fillStyle = currentTheme.text;
    ctx.font = "20px Arial";
    ctx.fillText(`Score: ${score} | High Score: ${highScore}`, 20, 30);

    if (gameOver) {
      ctx.fillText("Game Over - Press R to restart", WIDTH / 2 - 150, HEIGHT / 2);
    }
  };

  const drawCircle = (ctx, x, y, r, color) => {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  };

  useEffect(() => {
    const restart = e => {
      if (e.key === "r" && gameOver) {
        setScore(0);
        setGameOver(false);
        items.current = [];
        giants.current = [];
        obstacles.current = [];
        player.current.x = WIDTH / 2 - 25;
        setLastClap(0);
        setLastTheme(0);
        setModeIndex(0);
      }
    };
    window.addEventListener("keydown", restart);
    return () => window.removeEventListener("keydown", restart);
  }, [gameOver]);

  return (
    <div style={{ textAlign: "center" }}>
      <h1>1930 Game (React)</h1>
      <button onClick={() => setPaused(p => !p)}>Play / Pause</button>
      <canvas ref={canvasRef} width={WIDTH} height={HEIGHT} style={{ marginTop: 20 }} />
    </div>
  );
};

export default Game1930;
