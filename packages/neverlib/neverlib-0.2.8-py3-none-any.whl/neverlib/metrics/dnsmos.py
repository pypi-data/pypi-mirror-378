'''
Author: 凌逆战 | Never
Date: 2025-08-06 10:00:00
Description: 
要计算个性化 MOS 分数（干扰说话者受到惩罚），请提供“-p”参数，例如：python dnsmos.py -t ./SampleClips -o sample.csv -p
要计算常规 MOS 分数，请省略“-p”参数。例如：python dnsmos.py -t ./SampleClips -o sample.csv
'''
import librosa
import numpy as np
import onnxruntime
import soundfile as sf


class ComputeScore:
    def __init__(self, is_personalized_MOS, sr, input_length) -> None:
        self.sr = sr
        self.input_length = input_length
        self.is_personalized_MOS = is_personalized_MOS
        p808_model_path = "./DNSMOS/model_v8.onnx"
        if is_personalized_MOS:
            primary_model_path = "./pDNSMOS/sig_bak_ovr.onnx"
        else:
            primary_model_path = "./DNSMOS/sig_bak_ovr.onnx"

        self.onnx_sess = onnxruntime.InferenceSession(primary_model_path)
        self.p808_onnx_sess = onnxruntime.InferenceSession(p808_model_path)

    def audio_melspec(self, audio, n_mels=120, frame_size=320, hop_length=160, to_db=True):
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=self.sr, n_fft=frame_size + 1, hop_length=hop_length, n_mels=n_mels)
        if to_db:
            mel_spec = (librosa.power_to_db(mel_spec, ref=np.max) + 40) / 40
        return mel_spec.T

    def get_polyfit_val(self, sig, bak, ovr):
        if self.is_personalized_MOS:
            p_ovr = np.poly1d([-0.00533021, 0.005101, 1.18058466, -0.11236046])
            p_sig = np.poly1d([-0.01019296, 0.02751166, 1.19576786, -0.24348726])
            p_bak = np.poly1d([-0.04976499, 0.44276479, -0.1644611, 0.96883132])
        else:
            p_ovr = np.poly1d([-0.06766283, 1.11546468, 0.04602535])
            p_sig = np.poly1d([-0.08397278, 1.22083953, 0.0052439])
            p_bak = np.poly1d([-0.13166888, 1.60915514, -0.39604546])

        sig_poly, bak_poly, ovr_poly = p_sig(sig), p_bak(bak), p_ovr(ovr)

        return sig_poly, bak_poly, ovr_poly

    def __call__(self, wav_path):
        wav, wav_sr = sf.read(wav_path, dtype='float32')
        if wav_sr != self.sr:
            wav = librosa.resample(wav, wav_sr, self.sr)
        else:
            wav = wav
        len_samples = int(self.input_length * self.sr)
        while len(wav) < len_samples:
            wav = np.append(wav, wav)

        num_hops = int(np.floor(len(wav) / self.sr) - self.input_length) + 1
        hop_len_samples = self.sr
        predicted_mos_sig_seg_raw = []
        predicted_mos_bak_seg_raw = []
        predicted_mos_ovr_seg_raw = []
        predicted_mos_sig_seg = []
        predicted_mos_bak_seg = []
        predicted_mos_ovr_seg = []
        predicted_p808_mos = []

        for idx in range(num_hops):
            wav_seg = wav[int(idx * hop_len_samples): int((idx + self.input_length) * hop_len_samples)]
            if len(wav_seg) < len_samples:
                continue

            input_features = np.array(wav_seg)[np.newaxis, :]
            p808_input_features = np.array(self.audio_melspec(audio=wav_seg[:-160]))[np.newaxis, :, :]
            oi = {'input_1': input_features}
            p808_oi = {'input_1': p808_input_features}
            p808_mos = self.p808_onnx_sess.run(None, p808_oi)[0][0][0]
            mos_sig_raw, mos_bak_raw, mos_ovr_raw = self.onnx_sess.run(None, oi)[0][0]
            mos_sig, mos_bak, mos_ovr = self.get_polyfit_val(mos_sig_raw, mos_bak_raw, mos_ovr_raw)
            predicted_mos_sig_seg_raw.append(mos_sig_raw)
            predicted_mos_bak_seg_raw.append(mos_bak_raw)
            predicted_mos_ovr_seg_raw.append(mos_ovr_raw)
            predicted_mos_sig_seg.append(mos_sig)
            predicted_mos_bak_seg.append(mos_bak)
            predicted_mos_ovr_seg.append(mos_ovr)
            predicted_p808_mos.append(p808_mos)
        out_dict = {}
        out_dict['OVRL_raw'] = np.mean(predicted_mos_ovr_seg_raw)
        out_dict['SIG_raw'] = np.mean(predicted_mos_sig_seg_raw)
        out_dict['BAK_raw'] = np.mean(predicted_mos_bak_seg_raw)
        out_dict['OVRL'] = np.mean(predicted_mos_ovr_seg)
        out_dict['SIG'] = np.mean(predicted_mos_sig_seg)
        out_dict['BAK'] = np.mean(predicted_mos_bak_seg)
        out_dict['P808_MOS'] = np.mean(predicted_p808_mos)
        return out_dict


if __name__ == "__main__":
    SAMPLING_RATE = 16000
    INPUT_LENGTH = 9.01
    is_personalized_MOS = False
    testset_dir = "../data/vad_example.wav"

    compute_score = ComputeScore(is_personalized_MOS, SAMPLING_RATE, INPUT_LENGTH)
    data = compute_score(testset_dir)
    print(data)
