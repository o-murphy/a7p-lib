// my-script.mjs
console.log("Script path:", process.argv[1]);

if (process.argv.length > 2) {
  console.log("Arguments provided:");
  for (let i = 2; i < process.argv.length; i++) {
    console.log(`Argument ${i - 1}:`, process.argv[i]);
  }
} else {
  console.log("No arguments provided.");
}