class RemoteError extends Error {
    constructor(message, remoteStackTrace) {
        super(message);
        this.remoteStackTrace = remoteStackTrace;
    }

    toString() {
        return `Remote Error: ${this.message}\n${this.remoteStackTrace}`;
    }
};

export class Client {

    constructor(host, token) {
        this.hostName = host;
        this.securityToken = token;
        this.ws = null;
        this.listeners = new Set();
        this.wasError = false;
        this.reconnectDelay = 1000;
        this._call_id = 1;
        this._pendingCalls = new Map();

    }

    get next_call_id() {
        return this._call_id++;
    }

    get active() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    subscribe(handler) {
        this.listeners.add(handler);
    }

    unsubscribe(handler) {
        this.listeners.delete(handler);
    }

    unsubscribeAll() {
        this.listeners.clear();
    }

    _reconnect() {
        if (this.ws)
            window.setTimeout(() => this.connect(), this.reconnectDelay);
        }

    connect() {
        this.wasError = false;
        this.ws = new WebSocket(`ws://${this.hostName}/ws?token=${this.securityToken}`);
        this.ws.onerror = (evt) => {
            console.log(`WebSocket error `);
            //reconnect
            this.wasError = true;
            this._reconnect();
        };
        return new Promise((resolve, reject) => {
            this.ws.onopen = () => {

                this.ws.onopen = null;
                this.ws.onmessage = (evt) => this.processMessage(evt.data);
                this.ws.onclose = (evt) => {
                    console.log(`Websocket closed - clean ${evt.wasClean}, code ${evt.code}`);
                    document.dispatchEvent(new Event('ws-client-close'));
                    if (evt.code !== 1000 && !this.wasError) {
                        this._reconnect()
                    }
                }
                console.log('WS connected');
                resolve();
                document.dispatchEvent(new Event('ws-client-open'));
            }
        })
    }

    processMessage(msg) {
        console.log('Message: ' + msg);
        let data = JSON.parse(msg)
        let resolveCall = (action, value) => {
            let callData = this._pendingCalls.get(data.call_id);
            if (callData) {
                this._pendingCalls.delete(data.call_id);
                callData[action](value);
            } else {
                console.log(`Error: unmached call_id: ${call_id}`)
            }
        }
        switch (data.t) {
            case 'r':
                resolveCall('resolve', data.returned);
                break;
            case 'e':
                resolveCall('reject', new RemoteError(data.error, data.error_stack_trace));
                break;
            case 'm':
                this.listeners.forEach((handler) => handler(data.data));
        }
    }

    exec(args, kwargs) {
        if (this.ws.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket not ready');
        }
        let call_id = this.next_call_id;
        this.ws.send(JSON.stringify({call_id, args, kwargs}));
        return new Promise((resolve, reject) => {
            this._pendingCalls.set(call_id, {resolve, reject, ts: new Date()})
        })
    }

    close() {
        let ws = this.ws;
        this.ws = null;
        ws.close();
    }
};
