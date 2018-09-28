#!/usr/bin/env python3
from umbral import pre, keys, config
from nucypher import MockNetwork
import os
import sys
import argparse


def main(m, n, filenames):
    files = [open(filename, 'w') for filename in filenames]

    config.set_default_curve()

    alice_privkey = keys.UmbralPrivateKey.gen_key()
    alice_pubkey = alice_privkey.get_pubkey()

    bob_privkey = keys.UmbralPrivateKey.gen_key()
    bob_pubkey = bob_privkey.get_pubkey()

    mock_kms = MockNetwork()

    sys.stderr.write('Server with PID %s is ready to pipe messages.\n' % os.getpid())

    for line in sys.stdin:
        ciphertext, capsule = pre.encrypt(alice_pubkey, line.rstrip('\n').encode('utf8'))

        alice_kfrags = pre.split_rekey(alice_privkey, bob_pubkey, m, n)

        policy_id = mock_kms.grant(alice_kfrags)

        bob_cfrags = mock_kms.reencrypt(policy_id, capsule, m)

        bob_capsule = capsule
        for cfrag in bob_cfrags:
            bob_capsule.attach_cfrag(cfrag)

        decrypted = pre.decrypt(ciphertext, bob_capsule, bob_privkey, alice_pubkey)

        for file in files:
            file.write('%s\n' % decrypted.decode('utf8'))
            file.flush()

        mock_kms.revoke(policy_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=int, default=10)
    parser.add_argument('-n', type=int, default=20)
    parser.add_argument('filenames', metavar='FILE', nargs='+')

    args = parser.parse_args()

    main(args.m, args.n, args.filenames)
