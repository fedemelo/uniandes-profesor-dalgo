const readline = require("readline");

const rl = readline.createInterface({ input: process.stdin, terminal: false });
const lines = [];

rl.on("line", (line) => lines.push(line));

rl.on("close", () => {
  const casos = parseInt(lines[0], 10);
  const respuestas = [];

  for (let i = 0; i < casos; i++) {
    const numeros = lines[i + 1].trim().split(/\s+/).map(Number);
    let cp = 0;
    let sp = 0;
    for (const n of numeros) {
      if (n % 2 === 0) {
        cp++;
        sp += n;
      }
    }
    respuestas.push(`${cp} ${sp}`);
  }

  console.log(respuestas.join("\n"));
});
