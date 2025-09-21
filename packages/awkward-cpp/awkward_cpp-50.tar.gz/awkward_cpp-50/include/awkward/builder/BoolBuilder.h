// BSD 3-Clause License; see https://github.com/scikit-hep/awkward/blob/main/LICENSE

#ifndef AWKWARD_BOOLBUILDER_H_
#define AWKWARD_BOOLBUILDER_H_

#include <complex>
#include <string>

#include "awkward/common.h"
#include "awkward/BuilderOptions.h"
#include "awkward/GrowableBuffer.h"
#include "awkward/builder/Builder.h"

namespace awkward {

  /// @class BoolBuilder
  ///
  /// @brief Builder node that accumulates boolean values.
  class EXPORT_SYMBOL BoolBuilder: public Builder {
  public:
    /// @brief Create an empty BoolBuilder.
    /// @param options Configuration options for building an array;
    /// these are passed to every Builder's constructor.
    static const BuilderPtr
      fromempty(const BuilderOptions& options);

    /// @brief Create a BoolBuilder from a full set of parameters.
    ///
    /// @param options Configuration options for building an array;
    /// these are passed to every Builder's constructor.
    /// @param buffer Contains the accumulated boolean values.
    BoolBuilder(const BuilderOptions& options,
                GrowableBuffer<uint8_t> buffer);

    /// @brief User-friendly name of this class: `"BoolBuilder"`.
    const std::string
      classname() const override;

    const std::string
      to_buffers(BuffersContainer& container, int64_t& form_key_id) const override;

    int64_t
      length() const override;

    void
      clear() override;

    /// @copydoc Builder::active()
    ///
    /// A BoolBuilder is never active.
    bool
      active() const override;

    const BuilderPtr
      null() override;

    const BuilderPtr
      boolean(bool x) override;

    const BuilderPtr
      integer(int64_t x) override;

    const BuilderPtr
      real(double x) override;

    const BuilderPtr
      complex(std::complex<double> x) override;

    const BuilderPtr
      datetime(int64_t x, const std::string& unit) override;

    const BuilderPtr
      timedelta(int64_t x, const std::string& unit) override;

    const BuilderPtr
      string(const char* x, int64_t length, const char* encoding) override;

    const BuilderPtr
      beginlist() override;

    const BuilderPtr
      endlist() override;

    const BuilderPtr
      begintuple(int64_t numfields) override;

    const BuilderPtr
      index(int64_t index) override;

    const BuilderPtr
      endtuple() override;

    const BuilderPtr
      beginrecord(const char* name, bool check) override;

    void
      field(const char* key, bool check) override;

    const BuilderPtr
      endrecord() override;

    const BuilderOptions&
      options() const { return options_; }

    const GrowableBuffer<uint8_t>& buffer() const { return buffer_; }

  private:
    const BuilderOptions options_;
    GrowableBuffer<uint8_t> buffer_;
  };

}

#endif // AWKWARD_BOOLBUILDER_H_
