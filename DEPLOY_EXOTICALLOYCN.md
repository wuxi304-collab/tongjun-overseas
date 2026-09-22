# Deploy exoticalloycn.com

The final production target is **Tencent Cloud Lighthouse**, not Vercel.

Use:

- release branch: `release/v34.152-r15.26-tencent-lighthouse`
- deployment guide: `deploy/tencent/README.md`
- Nginx template: `deploy/tencent/nginx-exoticalloycn.conf.template`
- systemd template: `deploy/tencent/tongjun-api.service.template`
- environment template: `deploy/tencent/tongjun-overseas.env.example`
- server bootstrap: `deploy/tencent/bootstrap.sh`
- release deploy: `deploy/tencent/deploy.sh`

Architecture: Nginx serves the R15.26 static production build and proxies only `/api/*` to the Node service on `127.0.0.1:8787`.

Legacy Vercel configuration files remain in repository history for compatibility/reference but are not the production deployment path.
