////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2021-2024, CryptoLab Inc. All rights reserved.               //
//                                                                            //
// This software and/or source code may be commercially used and/or           //
// disseminated only with the written permission of CryptoLab Inc,            //
// or in accordance with the terms and conditions stipulated in the           //
// agreement/contract under which the software and/or source code has been    //
// supplied by CryptoLab Inc. Any unauthorized commercial use and/or          //
// dissemination of this file is strictly prohibited and will constitute      //
// an infringement of copyright.                                              //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

#pragma once

#include "EVI/Context.hpp"
#include "EVI/Enums.hpp"
#include "EVI/Export.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/Query.hpp"

#include <memory>
#include <string>
#include <vector>

namespace evi {

namespace detail {
class Encryptor;
} // namespace detail

/**
 * @class Encryptor
 * @brief Encodes or encrypts vectors into `Query` objects.
 *
 * An `Encryptor` produces `Query` instances representing either:
 * - `EncodeType::ITEM`  — encrypted database items
 * - `EncodeType::QUERY` — encoded/encrypted search queries
 */
class EVI_API Encryptor {
public:
    /// @brief Empty handle; initialize with makeEncryptor() before use.
    Encryptor() : impl_(nullptr) {}

    /**
     * @brief Constructs an Encryptor with an internal implementation.
     * @param impl Shared pointer to the internal `detail::Encryptor` object.
     */
    explicit Encryptor(std::shared_ptr<detail::Encryptor> impl) noexcept;

    /**
     * @brief Encodes a plaintext vector into a `Query`.
     * @param data Input vector to encode.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @return Encoded `Query` object.
     */
    Query encode(const std::vector<float> &data, evi::EncodeType type, int level = 0) const;

    /**
     * @brief Encodes a batch of plaintext vectors into `Query` objects.
     * @param data List of input vectors to encode.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @return List of encoded `Query` objects.
     */
    std::vector<Query> encode(const std::vector<std::vector<float>> &data, evi::EncodeType type, int level = 0) const;

    /**
     * @brief Encrypts a plaintext vector into a `Query`.
     * @param data Input vector to encrypt.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @return Encrypted `Query` object.
     */
    Query encrypt(const std::vector<float> &data, evi::EncodeType type, int level = 0) const;

    /**
     * @brief Encrypts a batch of vectors into `Query` objects.
     * @param data List of input vectors to encrypt.
     * @param type Encoding type (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @return List of encrypted `Query` objects.
     * @note Use this function only when `evalMode` is **FLAT**.
     */
    std::vector<Query> encrypt(const std::vector<std::vector<float>> &data, evi::EncodeType type, int level = 0) const;

    /**
     * @brief Encrypts multiple vectors in a batch and returns `Query` objects.
     * @param data List of input vectors to encrypt.
     * @param type Encoding type for all entries (`ITEM` or `QUERY`).
     * @param level Optional remaining multiplicative depth (default: 0).
     * @return Vector of encrypted `Query` objects.
     * @note Use this function only when `evalMode` is **RMP**.
     */
    std::vector<Query> encryptBulk(const std::vector<std::vector<float>> &data, evi::EncodeType type, int level = 0);

private:
    std::shared_ptr<detail::Encryptor> impl_;
};

EVI_API Encryptor makeEncryptor(const Context &context);

/**
 * @brief Creates an `Encryptor` using an existing `KeyPack`.
 *
 * @param context Context used for key initialization and device selection.
 * @param key_pack Key pack containing the necessary encryption key.
 * @return Configured `Encryptor` instance.
 */
EVI_API Encryptor makeEncryptor(const Context &context, const KeyPack &key_pack);

/**
 * @brief Creates an `Encryptor` by loading encryption key file.
 *
 * @param context Context used for key initialization and device selection.
 * @param file_path Path to the encryption key file.
 * @return Configured `Encryptor` instance.
 */
EVI_API Encryptor makeEncryptor(const Context &context, const std::string &file_path);

} // namespace evi
