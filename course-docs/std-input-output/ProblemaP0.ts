import * as readline from "readline";

const rl = readline.createInterface({ input: process.stdin, terminal: false });
const lines: string[] = [];

rl.on("line", (line: string) => lines.push(line));

rl.on("close", () => {
  const casos: number = parseInt(lines[0], 10);
  const respuestas: string[] = [];

  for (let i = 0; i < casos; i++) {
    const numeros: number[] = lines[i + 1].trim().split(/\s+/).map(Number);
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
