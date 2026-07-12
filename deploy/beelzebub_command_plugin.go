package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

// Drop-in helper for a Beelzebub command plugin.
// It posts the incoming attacker/session metadata to the simulator HTTP endpoint
// and returns the simulator output to the caller.
type CommandPlugin struct {
    baseURL string
    client  *http.Client
}

func NewCommandPlugin() *CommandPlugin {
    return &CommandPlugin{
        baseURL: "http://127.0.0.1:8080/command",
        client: &http.Client{Timeout: 3 * time.Second},
    }
}

func (cp *CommandPlugin) Execute(attackerIP, clientString, command string) (string, error) {
    payload := map[string]string{
        "attacker_ip": attackerIP,
        "client":      clientString,
        "command":     command,
    }

    body, err := json.Marshal(payload)
    if err != nil {
        return "", fmt.Errorf("marshal payload: %w", err)
    }

    req, err := http.NewRequest(http.MethodPost, cp.baseURL, bytes.NewReader(body))
    if err != nil {
        return "", fmt.Errorf("build request: %w", err)
    }
    req.Header.Set("Content-Type", "application/json")

    resp, err := cp.client.Do(req)
    if err != nil {
        return "", fmt.Errorf("post to simulator: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return "", fmt.Errorf("simulator returned status %d", resp.StatusCode)
    }

    var result struct {
        Output string `json:"output"`
    }
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return "", fmt.Errorf("decode response: %w", err)
    }

    return result.Output, nil
}
