import { registerHooks } from 'node:module';
const stub = new URL('./aws-stub.mjs', import.meta.url).href;
registerHooks({
  resolve(specifier, context, next) {
    if (specifier.startsWith('@aws-sdk/')) return { url: stub, shortCircuit: true };
    return next(specifier, context);
  },
});
