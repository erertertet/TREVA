const importObject = {
  imports: {
    imported_func: (arg: number) => {
      console.log(`Hello from JavaScript: ${arg}`);
    },
  },
};

WebAssembly.instantiateStreaming(fetch("simple_test.wasm"), importObject).then(
  (results) => {
    console.log(results);
  }
);
