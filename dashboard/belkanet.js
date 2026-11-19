// BelkaNet em JavaScript puro: a mesma rede de cnn/belkanet.py, só com a passagem direta
// (forward). Lê os pesos de window.BELKA_MODELO (dashboard/modelo.js).
(function (global) {
  "use strict";

  function b64ParaFloat32(b64) {
    var bin = typeof atob === "function" ? atob(b64) : Buffer.from(b64, "base64").toString("binary");
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new Float32Array(bytes.buffer);
  }

  // Convolução 3x3, padding 1, seguida de ReLU. Entrada e saída em HWC.
  // Pesos W com forma (Cin*9, Cout): linha = c*9 + ki*3 + kj.
  function conv3x3Relu(x, H, Wd, Cin, W, b, Cout) {
    var out = new Float32Array(H * Wd * Cout);
    for (var y = 0; y < H; y++) {
      for (var xx = 0; xx < Wd; xx++) {
        var o = (y * Wd + xx) * Cout;
        for (var f = 0; f < Cout; f++) out[o + f] = b[f];
        for (var ki = 0; ki < 3; ki++) {
          var yy = y + ki - 1;
          if (yy < 0 || yy >= H) continue;
          for (var kj = 0; kj < 3; kj++) {
            var xc = xx + kj - 1;
            if (xc < 0 || xc >= Wd) continue;
            var p = (yy * Wd + xc) * Cin;
            for (var c = 0; c < Cin; c++) {
              var v = x[p + c];
              if (v === 0) continue;
              var row = (c * 9 + ki * 3 + kj) * Cout;
              for (var g = 0; g < Cout; g++) out[o + g] += v * W[row + g];
            }
          }
        }
        for (var h = 0; h < Cout; h++) if (out[o + h] < 0) out[o + h] = 0;
      }
    }
    return out;
  }

  function maxPool2(x, H, Wd, C) {
    var h2 = H >> 1, w2 = Wd >> 1, out = new Float32Array(h2 * w2 * C);
    for (var y = 0; y < h2; y++) for (var xx = 0; xx < w2; xx++) for (var c = 0; c < C; c++) {
      var a = x[((2 * y) * Wd + 2 * xx) * C + c], b = x[((2 * y) * Wd + 2 * xx + 1) * C + c];
      var d = x[((2 * y + 1) * Wd + 2 * xx) * C + c], e = x[((2 * y + 1) * Wd + 2 * xx + 1) * C + c];
      out[(y * w2 + xx) * C + c] = Math.max(a, b, d, e);
    }
    return out;
  }

  function criar(modelo) {
    var P = modelo.pesos.map(function (p) { return b64ParaFloat32(p.b64); });
    var canais = [3].concat(modelo.canais), T = modelo.tam, K = modelo.classes.length;

    // x: Float32Array T*T*3 já normalizado -> probabilidades por classe
    function prever(x) {
      var H = T, a = x;
      for (var i = 0; i < modelo.canais.length; i++) {
        a = conv3x3Relu(a, H, H, canais[i], P[2 * i], P[2 * i + 1], canais[i + 1]);
        if (i < modelo.canais.length - 1) { a = maxPool2(a, H, H, canais[i + 1]); H >>= 1; }
      }
      var C = canais[canais.length - 1], gap = new Float32Array(C), n = H * H;
      for (var j = 0; j < n; j++) for (var c = 0; c < C; c++) gap[c] += a[j * C + c];
      for (var c2 = 0; c2 < C; c2++) gap[c2] /= n;
      var Wd = P[P.length - 2], bd = P[P.length - 1], z = new Float32Array(K), m = -Infinity;
      for (var k = 0; k < K; k++) {
        var s = bd[k];
        for (var c3 = 0; c3 < C; c3++) s += gap[c3] * Wd[c3 * K + k];
        z[k] = s; if (s > m) m = s;
      }
      var soma = 0, pr = new Float32Array(K);
      for (var k2 = 0; k2 < K; k2++) { pr[k2] = Math.exp(z[k2] - m); soma += pr[k2]; }
      for (var k3 = 0; k3 < K; k3++) pr[k3] /= soma;
      return pr;
    }

    // pixels RGBA (T*T*4, como vem do canvas) -> tensor normalizado; espelhar=true inverte na horizontal
    function normalizar(rgba, espelhar) {
      var x = new Float32Array(T * T * 3);
      for (var y = 0; y < T; y++) for (var xx = 0; xx < T; xx++) {
        var src = (y * T + (espelhar ? T - 1 - xx : xx)) * 4, dst = (y * T + xx) * 3;
        for (var c = 0; c < 3; c++) x[dst + c] = (rgba[src + c] / 255 - modelo.media[c]) / modelo.desvio[c];
      }
      return x;
    }

    // média da previsão da imagem e do seu espelho (deixa o resultado mais estável)
    function classificarRGBA(rgba) {
      var p1 = prever(normalizar(rgba, false)), p2 = prever(normalizar(rgba, true));
      return modelo.classes.map(function (nome, i) { return { classe: nome, prob: (p1[i] + p2[i]) / 2 }; })
        .sort(function (a, b) { return b.prob - a.prob; });
    }

    return { prever: prever, normalizar: normalizar, classificarRGBA: classificarRGBA };
  }

  global.BelkaNet = { criar: criar };
  if (typeof module !== "undefined") module.exports = global.BelkaNet;
})(typeof window !== "undefined" ? window : globalThis);
