// @ts-check

import { state, saveStateToStorage, setActiveSessionId } from "../core/state.js";
import * as api from "../core/api.js";
import { showToast } from "./toast.js";

function createOverlay() {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  return overlay;
}

function createModalShell(title) {
  const modal = document.createElement("div");
  modal.className = "modal";

  const header = document.createElement("div");
  header.className = "modal-header";
  header.innerHTML = `
    <h2>${title}</h2>
    <button class="modal-close" data-modal-close>&times;</button>
  `;

  const body = document.createElement("div");
  body.className = "modal-body";

  modal.appendChild(header);
  modal.appendChild(body);
  return { modal, body };
}

/**
 * @param {boolean} forceOpen
 * @returns {Promise<boolean>}
 */
export function showSettingsModal(forceOpen) {
  return new Promise((resolve) => {
    const overlay = createOverlay();
    const { modal, body } = createModalShell("设置");

    body.innerHTML = getSettingsContent();
    overlay.appendChild(modal);

    const closeBtns = modal.querySelectorAll("[data-modal-close]");
    if (forceOpen) closeBtns.forEach((b) => b.classList.add("hidden"));

    overlay.addEventListener("click", (ev) => {
      if (ev.target === overlay && !forceOpen) {
        overlay.remove();
        resolve(false);
      }
    });

    closeBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        if (!forceOpen) {
          overlay.remove();
          resolve(false);
        }
      });
    });

    modal.querySelector("#settingsSaveBtn")?.addEventListener("click", async () => {
      const ok = await saveSettings(modal);
      if (ok) {
        overlay.remove();
        resolve(true);
      }
    });

    document.body.appendChild(overlay);
  });
}

function getSettingsContent() {
  const provider = state.config.llm_provider || "deepseek";
  const apiKey = state.config.llm_api_key || "";
  const model = state.config.llm_model || "";
  const baseUrl = state.config.llm_base_url || "";
  const nickname = state.config.user_nickname || "";
  const emotionTheme = state.config.enable_emotion_theme !== "false";
  const debugMode = state.debugEnabled === true;

  return `
    <div class="modal-section">
      <div class="form-group">
        <label>服务商</label>
        <select id="settingsProvider">
          <option value="deepseek" ${
            provider === "deepseek" ? "selected" : ""
          }>DeepSeek</option>
          <option value="openai" ${
            provider === "openai" ? "selected" : ""
          }>OpenAI</option>
          <option value="anthropic" ${
            provider === "anthropic" ? "selected" : ""
          }>Anthropic</option>
          <option value="custom" ${
            provider === "custom" ? "selected" : ""
          }>自定义</option>
        </select>
      </div>
      <div class="form-group">
        <label>API Key</label>
        <input id="settingsApiKey" type="password" value="${apiKey}" placeholder="必填" />
      </div>
      <div class="form-group">
        <label>模型</label>
        <input id="settingsModel" type="text" value="${model}" placeholder="必填" />
      </div>
      <div class="form-group">
        <label>Base URL（仅自定义）</label>
        <input id="settingsBaseUrl" type="text" value="${baseUrl}" placeholder="https://..." />
      </div>
      <div class="form-group">
        <label>昵称</label>
        <input id="settingsNickname" type="text" value="${nickname}" />
      </div>
      <div class="form-group inline">
        <label>情绪主题</label>
        <label class="switch">
          <input id="settingsEmotionTheme" type="checkbox" ${
            emotionTheme ? "checked" : ""
          } />
          <span class="slider"></span>
        </label>
      </div>
      <div class="form-group inline">
        <label>调试模式</label>
        <label class="switch">
          <input id="settingsDebugMode" type="checkbox" ${
            debugMode ? "checked" : ""
          } />
          <span class="slider"></span>
        </label>
      </div>
      <div class="modal-actions">
        <button class="btn-primary" id="settingsSaveBtn">保存</button>
      </div>
    </div>
  `;
}

async function saveSettings(modal) {
  const provider = modal.querySelector("#settingsProvider")?.value;
  const apiKey = modal.querySelector("#settingsApiKey")?.value?.trim();
  const model = modal.querySelector("#settingsModel")?.value?.trim();
  const baseUrl = modal.querySelector("#settingsBaseUrl")?.value?.trim();
  const nickname = modal.querySelector("#settingsNickname")?.value?.trim();
  const emotionTheme = modal.querySelector("#settingsEmotionTheme")?.checked;
  const debugMode = modal.querySelector("#settingsDebugMode")?.checked;

  if (!provider || !apiKey || !model) {
    showToast("服务商、API Key 和模型为必填项。", "error");
    return false;
  }
  if (provider === "custom" && !baseUrl) {
    showToast("自定义服务商需要填写 Base URL。", "error");
    return false;
  }

  state.config.llm_provider = provider;
  state.config.llm_api_key = apiKey;
  state.config.llm_model = model;
  state.config.llm_base_url = baseUrl || "";
  state.config.user_nickname = nickname || "";
  state.config.enable_emotion_theme = String(Boolean(emotionTheme));
  state.debugEnabled = Boolean(debugMode);

  try {
    await api.updateConfig({
      llm_provider: provider,
      llm_api_key: apiKey,
      llm_model: model,
      llm_base_url: baseUrl || "",
      user_nickname: nickname || "",
      enable_emotion_theme: String(Boolean(emotionTheme)).toLowerCase(),
    });
    saveStateToStorage();
    window.dispatchEvent(
      new CustomEvent("debug-mode-changed", { detail: { enabled: debugMode } }),
    );
    showToast("设置已保存。", "success");
    return true;
  } catch {
    showToast("保存设置失败。", "error");
    return false;
  }
}

/**
 * @param {import("../core/types.js").Character} character
 */
export function showCharacterSettingsModal(character) {
  const overlay = createOverlay();
  const { modal, body } = createModalShell(`${character.name} 设置`);

  const readonly = character.is_builtin;
  body.innerHTML = `
    <div class="modal-section">
      ${
        readonly
          ? '<div class="modal-notice modal-notice-readonly">系统自带角色，仅可预览，不可编辑。</div>'
          : ""
      }
      <div class="form-group">
        <label>名称</label>
        <input id="charName" type="text" value="${character.name}" ${
          readonly ? "readonly" : ""
        } />
      </div>
      <div class="form-group">
        <label>头像 URL</label>
        <input id="charAvatar" type="text" value="${character.avatar || ""}" ${
          readonly ? "readonly" : ""
        } />
      </div>
      <div class="form-group">
        <label>人设</label>
        <textarea id="charPersona" rows="6" ${
          readonly ? "readonly" : ""
        }>${character.persona}</textarea>
      </div>
      <div class="modal-actions">
        ${
          readonly
            ? ""
            : '<button class="modal-btn modal-btn-danger" id="charDeleteBtn">删除角色</button>'
        }
        <button class="modal-btn modal-btn-primary" id="charSaveBtn" ${
          readonly ? "disabled" : ""
        }>保存</button>
      </div>
    </div>
  `;

  modal
    .querySelectorAll("[data-modal-close]")
    .forEach((btn) => btn.addEventListener("click", () => overlay.remove()));
  overlay.addEventListener("click", (ev) => {
    if (ev.target === overlay) overlay.remove();
  });

  modal.querySelector("#charSaveBtn")?.addEventListener("click", async () => {
    if (readonly) return;
    const name = modal.querySelector("#charName")?.value?.trim();
    const avatar = modal.querySelector("#charAvatar")?.value?.trim();
    const persona = modal.querySelector("#charPersona")?.value?.trim();
    if (!name || !persona || !avatar) {
      showToast("所有字段均为必填项。", "error");
      return;
    }
    try {
      const updated = await api.updateCharacter(character.id, {
        name,
        avatar,
        persona,
      });
      Object.assign(character, updated);
      saveStateToStorage();
      showToast("角色已更新。", "success");
      overlay.remove();
    } catch {
      showToast("更新角色失败。", "error");
    }
  });

  modal.querySelector("#charDeleteBtn")?.addEventListener("click", async () => {
    if (readonly) return;
    const ok = await showConfirmModal("删除该角色？此操作不可恢复。");
    if (!ok) return;

    try {
      await api.deleteCharacter(character.id);

      const sess = state.sessions.find((s) => s.character_id === character.id);
      const sessionId = sess?.id || null;

      state.characters = state.characters.filter((c) => c.id !== character.id);
      state.sessions = state.sessions.filter((s) => s.character_id !== character.id);

      if (sessionId) {
        state.messageCache.delete(sessionId);
        state.readTimestampBySession.delete(sessionId);
      }

      setActiveSessionId(null);
      saveStateToStorage();
      showToast("角色已删除。", "success");
      overlay.remove();

      window.dispatchEvent(
        new CustomEvent("character-deleted", {
          detail: { characterId: character.id, sessionId },
        }),
      );
    } catch {
      showToast("删除失败。", "error");
    }
  });

  overlay.appendChild(modal);
  document.body.appendChild(overlay);
}

/**
 * @returns {Promise<boolean>}
 */
export function showCreateCharacterModal() {
  return new Promise((resolve) => {
    const overlay = createOverlay();
    const { modal, body } = createModalShell("创建角色");

    body.innerHTML = `
      <div class="modal-section">
        <div class="form-group">
          <label>名称</label>
          <input id="newCharName" type="text" placeholder="必填" />
        </div>
        <div class="form-group">
          <label>头像 URL</label>
          <input id="newCharAvatar" type="text" placeholder="https://..." />
        </div>
        <div class="form-group">
          <label>人设</label>
          <textarea id="newCharPersona" rows="6" placeholder="必填"></textarea>
        </div>
        <div class="modal-actions">
          <button class="modal-btn modal-btn-secondary" data-modal-close>取消</button>
          <button class="modal-btn modal-btn-primary" id="newCharCreateBtn">创建</button>
        </div>
      </div>
    `;

    modal.querySelectorAll("[data-modal-close]").forEach((btn) =>
      btn.addEventListener("click", () => {
        overlay.remove();
        resolve(false);
      }),
    );
    overlay.addEventListener("click", (ev) => {
      if (ev.target === overlay) {
        overlay.remove();
        resolve(false);
      }
    });

    modal.querySelector("#newCharCreateBtn")?.addEventListener("click", async () => {
      const name = modal.querySelector("#newCharName")?.value?.trim();
      const avatar = modal.querySelector("#newCharAvatar")?.value?.trim();
      const persona = modal.querySelector("#newCharPersona")?.value?.trim();
      if (!name || !persona || !avatar) {
        showToast("所有字段均为必填项。", "error");
        return;
      }
      try {
        const created = await api.createCharacter({ name, avatar, persona });
        state.characters.push(created);
        state.sessions = await api.fetchSessions();
        saveStateToStorage();
        showToast("角色已创建。", "success");
        overlay.remove();
        resolve(true);
      } catch {
        showToast("创建角色失败。", "error");
      }
    });

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
  });
}

/**
 * @param {string} message
 * @returns {Promise<boolean>}
 */
export function showErrorModal(message) {
  return new Promise((resolve) => {
    const overlay = createOverlay();
    const { modal, body } = createModalShell("错误");
    body.innerHTML = `
      <p>${message}</p>
      <div class="modal-actions">
        <button class="btn-secondary" data-modal-close>取消</button>
        <button class="btn-primary" id="retryBtn">重试</button>
      </div>
    `;

    modal.querySelectorAll("[data-modal-close]").forEach((btn) =>
      btn.addEventListener("click", () => {
        overlay.remove();
        resolve(false);
      }),
    );
    modal.querySelector("#retryBtn")?.addEventListener("click", () => {
      overlay.remove();
      resolve(true);
    });

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
  });
}

/**
 * @param {string} message
 * @returns {Promise<boolean>}
 */
export function showConfirmModal(message) {
  return new Promise((resolve) => {
    const overlay = createOverlay();
    const { modal, body } = createModalShell("警告");
    body.innerHTML = `
      <div class="confirm-message">${message}</div>
      <div class="modal-actions">
        <button class="btn-secondary" data-modal-close>取消</button>
        <button class="modal-btn modal-btn-danger" id="confirmBtn">确认删除</button>
      </div>
    `;

    modal.querySelectorAll("[data-modal-close]").forEach((btn) =>
      btn.addEventListener("click", () => {
        overlay.remove();
        resolve(false);
      }),
    );
    modal.querySelector("#confirmBtn")?.addEventListener("click", () => {
      overlay.remove();
      resolve(true);
    });

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
  });
}
