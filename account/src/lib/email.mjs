/**
 * Sends the sign-in code by email via SES.
 *
 * Before SES is verified (or for local testing) leave MAIL_FROM unset — the
 * code is written to CloudWatch logs instead of sent, so the flow still works.
 */

import { SESClient, SendEmailCommand } from '@aws-sdk/client-ses';

const ses = new SESClient({});
const FROM = process.env.MAIL_FROM || '';

export async function sendCode(email, code) {
  if (!FROM) {
    console.log(`[no MAIL_FROM] sign-in code for ${email}: ${code}`);
    return;
  }
  await ses.send(new SendEmailCommand({
    Source: `San Diego Institute of Technology <${FROM}>`,
    Destination: { ToAddresses: [email] },
    Message: {
      Subject: { Data: `Your SDIT sign-in code: ${code}` },
      Body: {
        Text: {
          Data:
            `Your sign-in code is ${code}\n\n` +
            `It expires in 10 minutes. If you didn't ask to sign in, ignore this email.`,
        },
      },
    },
  }));
}
